"""
Retail-Policy Prompt Builder
============================

Concrete :class:`data_generator.tool.DataGeneratorTool` implementation that
authors realistic retail store-policy documents (returns, refunds, shipping,
warranty, privacy) shaped for ingestion into an Azure AI Search index. Each
record is emitted as a flat document with an ``id`` / ``title`` / ``content``
triplet plus a ``contentVector`` embedding so the workshop's Foundry IQ
knowledge source can perform hybrid search.
"""

from __future__ import annotations

import argparse
import json
import logging
import random
import uuid
from datetime import datetime, timezone
from typing import Any

import yaml

from ..tool import DataGeneratorTool

_logger = logging.getLogger(__name__)


class RetailPolicyTool(DataGeneratorTool):
    """Generate synthetic, search-index-ready retail store-policy documents."""

    # ------------------------------------------------------------------ #
    # Identification / registry key                                      #
    # ------------------------------------------------------------------ #
    name: str = "retail-policy"
    toolName: str = "RetailPolicy"

    # ------------------------------------------------------------------ #
    # Policy taxonomy                                                    #
    # ------------------------------------------------------------------ #
    _POLICY_TYPES: list[str] = [
        "returns",
        "refunds",
        "shipping",
        "warranty",
        "privacy",
        "loyalty",
    ]

    # ------------------------------------------------------------------ #
    # CLI contract                                                       #
    # ------------------------------------------------------------------ #
    def __init__(self, *, industry: str | None = None) -> None:
        """Create a new tool instance with an optional *industry* override."""
        super().__init__()
        self.industry = industry or "general"

    def cli_arguments(self) -> list[dict[str, Any]]:
        """Argparse specification consumed by the top-level CLI wrapper."""
        return [
            {
                "flags": ["-i", "--industry"],
                "kwargs": {
                    "required": False,
                    "metavar": "TEXT",
                    "default": "general",
                    "help": (
                        "Industry/theme for the policies (e.g. electronics, fashion)."
                    ),
                },
            }
        ]

    def validate_args(self, ns: argparse.Namespace) -> None:
        """Persist validated CLI arguments onto the instance."""
        self.industry = ns.industry or "general"

    def examples(self) -> list[str]:
        """Representative usage snippets for `--help` output."""
        return [
            "python -m data_generator "
            "--scenario retail-policy "
            "--count 20 "
            "--industry supermarket "
            "--output-format json "
            "--out-file shared/data/retail-policies.jsonl"
        ]

    # ------------------------------------------------------------------ #
    # Output formats                                                     #
    # ------------------------------------------------------------------ #
    def supported_output_formats(self) -> list[str]:
        """Return the list of output formats this tool can generate."""
        return ["yaml", "json", "text"]

    # ------------------------------------------------------------------ #
    # Prompt construction                                                #
    # ------------------------------------------------------------------ #
    def _prompt_common(self, *, unique_id: str | None = None) -> str:
        """Shared prompt header including an optional caller-supplied id."""
        policy_id = unique_id or str(uuid.uuid4())
        effective_date = datetime.now(timezone.utc).date().isoformat()
        policy_type = random.choice(self._POLICY_TYPES)
        return (
            f"Policy ID (immutable): {policy_id}\n"
            f"Effective Date: {effective_date}\n"
            f"Policy Type: {policy_type}\n"
            f"Industry Theme: {self.industry}\n\n"
        )

    def build_prompt(self, output_format: str, *, unique_id: str | None = None) -> str:
        """Return the full prompt for the requested *output_format*."""
        base = (
            "You are a retail operations specialist drafting REALISTIC BUT "
            "ENTIRELY FICTIONAL customer-facing store policy documents.\n\n"
            f"{self._prompt_common(unique_id=unique_id)}"
            "Write a clear, professional policy of 150-300 words that a customer "
            "or support agent could rely on. Always output ONLY the requested "
            "data structure - no markdown fences, no commentary.\n\n"
        )

        if output_format == "yaml":
            return base + self._yaml_skeleton()
        if output_format == "json":
            return base + self._json_skeleton()
        # TEXT
        return base + self._text_skeleton()

    # ------------------------------------------------------------------ #
    # Static prompt fragments                                            #
    # ------------------------------------------------------------------ #
    def _yaml_skeleton(self) -> str:
        """YAML response schema instructing the LLM on the exact shape."""
        return (
            "Return valid YAML ONLY.\n\n"
            "policy_id: (echo above)\n"
            "effective_date: (echo above)\n"
            "policy_type: (echo above)\n"
            "title: concise policy title\n"
            f"category: relevant category for {self.industry}\n"
            "content: full policy text (150-300 words)\n"
        )

    def _json_skeleton(self) -> str:
        """JSON response schema instructing the LLM on the exact shape."""
        return (
            "Return valid JSON ONLY.\n\n"
            "{\n"
            '  "policy_id": "(echo above)",\n'
            '  "effective_date": "(echo above)",\n'
            '  "policy_type": "(echo above)",\n'
            '  "title": "Concise policy title",\n'
            f'  "category": "Relevant category for {self.industry}",\n'
            '  "content": "Full policy text (150-300 words)"\n'
            "}\n"
        )

    @staticmethod
    def _text_skeleton() -> str:
        """Plain-text layout for tools that prefer unstructured output."""
        return (
            "Return plain text WITHOUT YAML/JSON markers.\n\n"
            "Policy ID: (echo above)\n"
            "Effective Date: (echo above)\n"
            "Policy Type: (echo above)\n"
            "Title: Concise policy title\n"
            "Category: Relevant category\n"
            "Content: Full policy text (150-300 words)\n"
        )

    # ------------------------------------------------------------------ #
    # Post-processing                                                    #
    # ------------------------------------------------------------------ #
    def post_process(self, raw: str, output_format: str) -> Any:  # noqa: ANN401
        """Deserialize and reshape into a search-index document."""
        fmt = output_format.lower()
        parsed_data: Any

        if fmt == "json":
            try:
                parsed_data = json.loads(raw)
            except json.JSONDecodeError:
                _logger.warning(
                    "Failed to parse raw output as JSON. Returning raw string."
                )
                return raw
        elif fmt == "yaml":
            try:
                parsed_data = yaml.safe_load(raw)
            except yaml.YAMLError:
                _logger.warning(
                    "Failed to parse raw output as YAML. Returning raw string."
                )
                return raw
        # Handle both 'txt' (from CLI) and 'text' (from supported_output_formats)
        elif fmt in {"txt", "text"}:
            return raw
        else:
            _logger.warning(
                "Unknown output format '%s' for post-processing. Returning raw string.",
                output_format,
            )
            return raw

        if not isinstance(parsed_data, dict):
            return parsed_data

        return self._to_index_document(parsed_data)

    def _to_index_document(self, policy: dict[str, Any]) -> dict[str, Any]:
        """Reshape a parsed policy dict into a flat search-index document."""
        policy_id = str(policy.get("policy_id") or uuid.uuid4())
        title = str(policy.get("title", "")).strip()
        content = str(policy.get("content", "")).strip()
        return {
            "id": policy_id,
            "title": title,
            "content": content,
            "policyType": policy.get("policy_type", ""),
            "category": str(policy.get("category", "")).strip(),
            "effectiveDate": policy.get("effective_date"),
        }

    # ------------------------------------------------------------------ #
    # Embedding hooks                                                    #
    # ------------------------------------------------------------------ #
    def embedding_input(self, record: Any) -> str | None:  # noqa: ANN401
        """Embed the policy ``content`` for hybrid search."""
        if isinstance(record, dict):
            content = record.get("content")
            if isinstance(content, str) and content:
                return content
        return None

    # ------------------------------------------------------------------ #
    # Misc.                                                              #
    # ------------------------------------------------------------------ #
    def get_system_description(self) -> str:
        """Return a sentence describing the target retail policy set."""
        return f"Retail store policies for {self.industry}"
