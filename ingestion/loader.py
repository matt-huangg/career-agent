"""Load raw personal data files from the data/ directory."""

import csv
import json
from pathlib import Path


def load_documents(data_dir: str = "./data") -> list[dict]:
    """
    Walk the data directory and load JSON and CSV files.
    Returns a list of dicts with keys: source, content.
    """
    documents = []
    root = Path(data_dir)

    for path in root.rglob("*.json"):
        if not path.is_file():
            continue

        data = json.loads(path.read_text())
        content = json.dumps(data, indent=2)
        documents.append({"source": str(path), "content": content})

    for path in root.rglob("*.csv"):
        if not path.is_file():
            continue

        with path.open(newline="") as f:
            rows = list(csv.DictReader(f))
        content = "\n".join(str(row) for row in rows)
        documents.append({"source": str(path), "content": content})

    return documents


if __name__ == "__main__":
    docs = load_documents()
    print(f"Loaded {len(docs)} document(s)")
    for doc in docs:
        print(f"  {doc['source']} ({len(doc['content'])} chars)")
