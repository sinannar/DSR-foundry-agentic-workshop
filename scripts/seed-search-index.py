"""Seed shared Azure AI Search index with sample workshop documents."""

from __future__ import annotations

import json
import os
from pathlib import Path

from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchFieldDataType,
    SearchableField,
    SimpleField,
)


def _load_documents(path: Path) -> list[dict[str, str]]:
    docs: list[dict[str, str]] = []
    for line in path.read_text(encoding='utf-8').splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        docs.append(json.loads(stripped))
    return docs


def _build_credential() -> AzureKeyCredential | DefaultAzureCredential:
    admin_key = os.getenv('AZURE_SEARCH_ADMIN_KEY', '').strip()
    if admin_key:
        return AzureKeyCredential(admin_key)
    return DefaultAzureCredential(exclude_interactive_browser_credential=False)


def _ensure_index(index_client: SearchIndexClient, index_name: str) -> None:
    existing = {index.name for index in index_client.list_indexes()}
    if index_name in existing:
        return

    index = SearchIndex(
        name=index_name,
        fields=[
            SimpleField(name='id', type=SearchFieldDataType.String, key=True),
            SearchableField(name='title', type=SearchFieldDataType.String),
            SearchableField(name='content', type=SearchFieldDataType.String),
        ],
    )
    index_client.create_index(index)


def main() -> int:
    service_name = os.getenv('AZURE_SEARCH_SERVICE_NAME', '').strip()
    if not service_name:
        print('AZURE_SEARCH_SERVICE_NAME is not set. Skipping search index seed.')
        return 0

    index_name = os.getenv('SEARCH_INDEX_NAME', 'workshop-documents').strip()
    data_path = Path(__file__).resolve().parents[1] / 'shared' / 'data' / 'search-documents.jsonl'
    if not data_path.exists():
        print(f'Data file not found: {data_path}')
        return 1

    endpoint = f'https://{service_name}.search.windows.net'
    credential = _build_credential()
    index_client = SearchIndexClient(endpoint=endpoint, credential=credential)

    _ensure_index(index_client=index_client, index_name=index_name)

    search_client = SearchClient(endpoint=endpoint, index_name=index_name, credential=credential)
    docs = _load_documents(data_path)
    if not docs:
        print('No documents found to upload.')
        return 0

    results = search_client.upload_documents(documents=docs)
    failed = [r.key for r in results if not r.succeeded]
    if failed:
        print(f'Upload completed with failures. Failed document IDs: {", ".join(failed)}')
        return 1

    print(f'Uploaded {len(results)} documents to index {index_name}.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
