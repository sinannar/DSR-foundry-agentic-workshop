"""Seed shared Azure AI Search index with sample workshop documents."""

from pathlib import Path


def main() -> None:
    path = Path(__file__).resolve().parents[1] / 'shared' / 'data' / 'search-documents.jsonl'
    print(f"TODO: implement index seed using {path}")


if __name__ == '__main__':
    main()
