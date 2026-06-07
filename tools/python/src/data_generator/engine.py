"""
This module provides the :class:`DataGenerator` class, which orchestrates the
end-to-end synthetic-data generation process using Azure OpenAI through the
Microsoft Agent Framework.

It includes prompt-driven generation, optional embedding enrichment for
search-index-ready records, asynchronous execution with bounded concurrency,
and output persistence in several formats (per-record files or an aggregated
JSON Lines file).
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any, Final

import yaml
from agent_framework import Agent
from agent_framework.openai import (
    OpenAIChatCompletionClient,
    OpenAIEmbeddingClient,
)
from azure.identity import AzureCliCredential
from azure.identity.aio import AzureCliCredential as AsyncAzureCliCredential
from dotenv import load_dotenv

from data_generator.tool import DataGeneratorTool

__all__: list[str] = ["DataGenerator"]

_DEFAULT_LOG_FORMAT: Final[str] = "%(asctime)s %(levelname)-8s %(name)s :: %(message)s"
_LOGGER_NAME: Final[str] = "data-generator"


class DataGenerator:  # pylint: disable=too-many-instance-attributes
    """
    Orchestrates end-to-end synthetic-data generation.

    Parameters
    ----------
    tool:
        Concrete implementation of :class:`data_generator.tool.DataGeneratorTool`
        responsible for domain-specific prompt construction and post-processing.
    log_level:
        Logging verbosity passed straight to :pymod:`logging`.
    azure_openai_endpoint / azure_openai_deployment / azure_openai_api_key /
    azure_openai_api_version / azure_openai_embedding_deployment :
        Connection details for Azure OpenAI. Each can be provided as an explicit
        argument or via the corresponding environment variable.
    """

    # ------------------------------------------------------------------ #
    # Internal helpers                                                   #
    # ------------------------------------------------------------------ #
    @staticmethod
    def _env_or_override(override: str | None, env_var: str) -> str | None:
        """Return *override* if supplied, otherwise ``os.getenv(env_var)``."""
        return override or os.getenv(env_var)

    def __init__(                       # noqa: PLR0913
        self,
        tool: DataGeneratorTool,
        *,
        log_level: str | int = "INFO",
        azure_openai_endpoint: str | None = None,
        azure_openai_deployment: str | None = None,
        azure_openai_api_key: str | None = None,
        azure_openai_api_version: str | None = None,
        azure_openai_embedding_deployment: str | None = None,
    ) -> None:
        self.tool = tool
        load_dotenv()  # Load .env from CWD or parent (no error if missing)

        # ---- Resolve connection settings --------------------------------- #
        self.azure_openai_endpoint = self._env_or_override(
            azure_openai_endpoint, "AZURE_OPENAI_ENDPOINT"
        )
        self.azure_openai_deployment = self._env_or_override(
            azure_openai_deployment, "AZURE_OPENAI_DEPLOYMENT"
        )
        self.azure_openai_api_key = self._env_or_override(
            azure_openai_api_key, "AZURE_OPENAI_API_KEY"
        )
        self.azure_openai_api_version = self._env_or_override(
            azure_openai_api_version, "AZURE_OPENAI_API_VERSION"
        )
        self.azure_openai_embedding_deployment = self._env_or_override(
            azure_openai_embedding_deployment, "AZURE_OPENAI_EMBEDDING_DEPLOYMENT"
        )

        if not self.azure_openai_endpoint or not self.azure_openai_deployment:
            raise OSError(
                "Azure OpenAI connection details missing. "
                "Set --azure-openai-endpoint & --azure-openai-deployment CLI flags\n"
                "or AZURE_OPENAI_ENDPOINT / AZURE_OPENAI_DEPLOYMENT env variables."
            )

        # ------------------------------------------------------------------ #
        # Logging configuration                                              #
        # ------------------------------------------------------------------ #
        if not logging.getLogger().handlers:          # prevent duplicate handlers
            logging.basicConfig(format=_DEFAULT_LOG_FORMAT, level=log_level)
        self.logger = logging.getLogger(_LOGGER_NAME)
        self.logger.debug(
            "Using Azure OpenAI endpoint '%s', chat deployment '%s'.",
            self.azure_openai_endpoint,
            self.azure_openai_deployment,
        )

        # ------------------------------------------------------------------ #
        # Microsoft Agent Framework initialisation                           #
        # ------------------------------------------------------------------ #
        self._chat_credential = AzureCliCredential()
        self._agent = self._create_agent()

        # Embedding client is created lazily (only when a tool requests it).
        self._embedding_client: OpenAIEmbeddingClient | None = None
        self._embedding_credential: AsyncAzureCliCredential | None = None

    def _create_agent(self) -> Agent:
        """
        Instantiate an Agent Framework :class:`Agent` backed by Azure OpenAI.

        Authentication selects an API key when one is supplied, otherwise it
        falls back to ``AzureCliCredential`` (run ``az login`` beforehand).

        Returns
        -------
        agent_framework.Agent
            A ready-to-run agent for single-turn record generation.
        """
        client_kwargs: dict[str, Any] = {
            "model": self.azure_openai_deployment,
            "azure_endpoint": self.azure_openai_endpoint,
        }
        if self.azure_openai_api_version:
            client_kwargs["api_version"] = self.azure_openai_api_version
        if self.azure_openai_api_key:
            self.logger.debug("Authenticating to Azure OpenAI with API key.")
            client_kwargs["api_key"] = self.azure_openai_api_key
        else:
            self.logger.debug(
                "Authenticating to Azure OpenAI with AzureCliCredential."
            )
            client_kwargs["credential"] = self._chat_credential

        client = OpenAIChatCompletionClient(**client_kwargs)
        instructions = (
            self.tool.get_system_description()
            or f"{self.tool.toolName} synthetic-record generator."
        )
        return Agent(
            client=client,
            name=f"{self.tool.toolName}Generator",
            instructions=instructions,
        )

    # --------------------------------------------------------------------- #
    # Public façades                                                        #
    # --------------------------------------------------------------------- #
    def run(                            # noqa: PLR0913
        self,
        *,
        count: int,
        out_dir: Path | None = None,
        out_file: Path | None = None,
        output_format: str = "json",
        concurrency: int = 8,
        timeout_seconds: float | None = 300.0,
    ) -> None:
        """
        Blocking helper that delegates to the async implementation.

        Parameters
        ----------
        count:
            Number of records to generate.
        out_dir:
            Destination folder for per-record files. Mutually optional with
            *out_file*; at least one must be supplied.
        out_file:
            Destination JSON Lines file. When supplied, every record is written
            as one line to a single aggregated file (ideal for search-index
            ingestion) instead of per-record files.
        output_format:
            One of ``json``, ``yaml`` or ``txt``.
        concurrency:
            Upper bound on simultaneous Azure OpenAI requests.
        timeout_seconds:
            Maximum time in seconds to wait for a single generation task.
            If None, no timeout is applied.
        """
        if out_dir is None and out_file is None:
            raise ValueError("Either out_dir or out_file must be provided.")
        asyncio.run(
            self._run_async(
                count=count,
                out_dir=out_dir,
                out_file=out_file,
                output_format=output_format,
                concurrency=concurrency,
                timeout_seconds=timeout_seconds,
            )
        )

    # --------------------------------------------------------------------- #
    # Async methods                                                         #
    # --------------------------------------------------------------------- #
    async def _run_async(             # noqa: PLR0913
        self,
        *,
        count: int,
        out_dir: Path | None,
        out_file: Path | None,
        output_format: str,
        concurrency: int,
        timeout_seconds: float | None,
    ) -> None:
        """
        Drive *count* asynchronous generation tasks while honouring
        *concurrency* and an optional *timeout_seconds* per task.

        When *out_file* is supplied the generated records are collected in
        memory and flushed to a single JSON Lines file at the end.

        See Also
        --------
        _generate_one_async : Handles the life-cycle of a single record.
        """
        semaphore = asyncio.Semaphore(concurrency)
        collected: list[Any] | None = [] if out_file is not None else None
        tasks: list[asyncio.Task[None]] = []
        for i in range(1, count + 1):
            coro = self._generate_one_async(
                index=i,
                out_dir=out_dir,
                output_format=output_format,
                semaphore=semaphore,
                collected=collected,
            )
            if timeout_seconds is not None:
                task_coro = asyncio.wait_for(coro, timeout=timeout_seconds)
            else:
                task_coro = coro
            tasks.append(asyncio.create_task(task_coro))

        failures = 0
        for t in asyncio.as_completed(tasks):
            try:
                await t
            except asyncio.TimeoutError:
                self.logger.error(
                    "Generation task timed out after %s seconds.", timeout_seconds
                )
                failures += 1
            except Exception:  # pylint: disable=broad-exception-caught
                self.logger.exception("Generation task failed")
                failures += 1

        if collected is not None and out_file is not None:
            await asyncio.to_thread(self._write_jsonl, collected, out_file)

        await self._aclose_embedding_client()

        self.logger.info(
            "Generation finished. Success: %s, Failed: %s",
            count - failures,
            failures,
        )

    async def _generate_one_async(    # noqa: PLR0913
        self,
        *,
        index: int,
        out_dir: Path | None,
        output_format: str,
        semaphore: asyncio.Semaphore,
        collected: list[Any] | None,
    ) -> None:
        """
        Generate, post-process, optionally embed, and persist a single record.

        Parameters
        ----------
        index :
            Ordinal number of the record being produced (1-based).
        out_dir :
            Target directory for per-record output (ignored when *collected*
            is not None).
        output_format :
            File format - ``json``, ``yaml`` or ``txt``.
        semaphore :
            Synchronisation primitive controlling overall concurrency.
        collected :
            When supplied, the processed record is appended here for later
            aggregation instead of being written to a per-record file.
        """
        async with semaphore:
            unique_id = self.tool.get_unique_id()       # use tool-provided id
            prompt = self.tool.build_prompt(
                output_format,
                unique_id=unique_id,                    # pass to prompt builder
            )
            response = await self._agent.run(prompt)
            raw_output = getattr(response, "text", None) or str(response)
            processed = self.tool.post_process(raw_output, output_format)

            # Optional embedding enrichment for search-index-ready records.
            embed_text = self.tool.embedding_input(processed)
            if embed_text:
                vector = await self._embed(embed_text)
                processed = self.tool.attach_embedding(processed, vector)

            if collected is not None:
                collected.append(processed)
            else:
                await asyncio.to_thread(
                    self._persist,
                    unique_id=unique_id,
                    data=processed,
                    out_dir=out_dir,
                    output_format=output_format,
                )
            self.logger.debug("Record %s generated.", index)

    # --------------------------------------------------------------------- #
    # Embedding helpers                                                     #
    # --------------------------------------------------------------------- #
    async def _embed(self, text: str) -> list[float]:
        """Return the embedding vector for *text* using Azure OpenAI."""
        if self._embedding_client is None:
            if not self.azure_openai_embedding_deployment:
                raise OSError(
                    "Embedding deployment missing. "
                    "Set --embedding-deployment CLI flag\n"
                    "or AZURE_OPENAI_EMBEDDING_DEPLOYMENT env variable."
                )
            self._embedding_credential = AsyncAzureCliCredential()
            embedding_kwargs: dict[str, Any] = {
                "model": self.azure_openai_embedding_deployment,
                "azure_endpoint": self.azure_openai_endpoint,
                "credential": self._embedding_credential,
            }
            if self.azure_openai_api_version:
                embedding_kwargs["api_version"] = self.azure_openai_api_version
            self._embedding_client = OpenAIEmbeddingClient(**embedding_kwargs)
            self.logger.debug(
                "Created embedding client for deployment '%s'.",
                self.azure_openai_embedding_deployment,
            )

        result = await self._embedding_client.get_embeddings([text])
        return list(result[0].vector)

    async def _aclose_embedding_client(self) -> None:
        """Close the async embedding credential, if one was created."""
        if self._embedding_credential is not None:
            await self._embedding_credential.close()
            self._embedding_credential = None
            self._embedding_client = None

    # --------------------------------------------------------------------- #
    # Persistence helpers                                                   #
    # --------------------------------------------------------------------- #
    def _persist(
        self,
        *,
        data: Any,
        out_dir: Path,
        output_format: str,
        unique_id: str | None = None,
        index: int | None = None,
    ) -> None:
        """
        Persist **data** to a single per-record file using *output_format*.

        Parameters
        ----------
        data:
            Already post-processed object (dict / str / etc.).
        out_dir:
            Target directory. Created on-the-fly if it does not exist.
        output_format:
            ``json``, ``yaml``, ``txt`` or anything else handled by the default
            branch which falls back to ``str(data)``.
        unique_id:
            Tool-provided identifier used when naming the output file.
        index:
            1-based ordinal used when *unique_id* is unavailable.
        """
        out_dir.mkdir(parents=True, exist_ok=True)
        if unique_id:
            filename = f"{self.tool.toolName}_{unique_id}.{output_format}"
        elif index is not None:
            filename = f"{index:04d}.{output_format}"
        else:
            raise ValueError("Either unique_id or index must be provided.")
        file_path = out_dir / filename

        match output_format:
            case "json":
                with file_path.open("w", encoding="utf-8") as fp:
                    json.dump(data, fp, indent=2)
            case "yaml":
                with file_path.open("w", encoding="utf-8") as fp:
                    yaml.safe_dump(data, fp, sort_keys=False)
            case "txt":
                with file_path.open("w", encoding="utf-8") as fp:
                    fp.write(str(data))
            case _:
                with file_path.open("w", encoding="utf-8") as fp:
                    fp.write(str(data))

    @staticmethod
    def _write_jsonl(records: list[Any], out_file: Path) -> None:
        """Write *records* as a JSON Lines file (one JSON object per line)."""
        out_file.parent.mkdir(parents=True, exist_ok=True)
        with out_file.open("w", encoding="utf-8") as fp:
            for record in records:
                fp.write(json.dumps(record, ensure_ascii=False))
                fp.write("\n")

    # --------------------------------------------------------------------- #
    # Backwards-compat / simple sync loop                                   #
    # --------------------------------------------------------------------- #
    def generate_data(  # retained for compatibility; delegates to async path
        self,
        count: int,
        out_dir: Path,
        output_format: str = "json",
    ) -> None:
        """
        Backwards-compatibility shim calling :py:meth:`run`.

        Maintained for legacy scripts that expect a synchronous API.
        """
        self.run(
            count=count,
            out_dir=out_dir,
            output_format=output_format,
        )
