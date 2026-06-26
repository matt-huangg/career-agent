"""Load raw personal data files from the data/ directory."""

import csv
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Messages older than this are excluded to keep context recent and relevant
MESSAGES_LOOKBACK_DAYS = 365


def _filter_messages(rows: list[dict]) -> list[dict]:
    """
    Filter LinkedIn messages rows.
    Excludes sponsored conversations and messages older than MESSAGES_LOOKBACK_DAYS.
    """
    cutoff = datetime.now(tz=timezone.utc) - timedelta(days=MESSAGES_LOOKBACK_DAYS)
    filtered = []
    for row in rows:
        # Sponsored conversations are noise — LinkedIn promotional DMs
        if row.get("CONVERSATION TITLE", "").strip() == "Sponsored Conversation":
            continue

        # Parse the DATE column; skip rows with missing or unparseable dates
        raw_date = row.get("DATE", "").strip()
        try:
            msg_date = datetime.strptime(raw_date, "%Y-%m-%d %H:%M:%S %Z").replace(
                tzinfo=timezone.utc
            )
        except ValueError:
            continue

        if msg_date >= cutoff:
            filtered.append(row)

    return filtered


def load_documents(data_dir: str = "./data") -> list[dict]:
    """
    Walk the data directory and load JSON and CSV files.
    Returns a list of dicts with keys: source, content.
    Applies message filtering for messages.csv to exclude noise.
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

        # Apply message-specific filters to reduce noise from LinkedIn DMs
        if path.name == "messages.csv":
            before = len(rows)
            rows = _filter_messages(rows)
            print(f"  [messages.csv] {before} rows → {len(rows)} after filtering")

        content = "\n".join(str(row) for row in rows)
        documents.append({"source": str(path), "content": content})

    return documents


if __name__ == "__main__":
    docs = load_documents()
    print(f"Loaded {len(docs)} document(s)")
    for doc in docs:
        print(f"  {doc['source']} ({len(doc['content'])} chars)")
