"""Entry point for the Career Agent."""

import sys
from dotenv import load_dotenv
from ingestion import load_documents, chunk_documents, embed_and_store
from agent import run_agent

load_dotenv()


def ingest():
    """
    Run the full ingestion pipeline over the data/ directory.

    TODO:
    - Call load_documents() to load files from data/
    - Call chunk_documents() to split into token-bounded chunks
    - Call embed_and_store() to embed and persist to ChromaDB
    """
    pass


def query(q: str):
    """
    Run the agent against the knowledge base and print the result.

    TODO:
    - Call run_agent() with the query string
    - Print the structured CareerInsight fields to stdout
    """
    pass


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python main.py ingest              # index your data/")
        print('  python main.py query "your question here"')
        sys.exit(1)

    command = sys.argv[1]

    if command == "ingest":
        ingest()
    elif command == "query" and len(sys.argv) > 2:
        query(sys.argv[2])
    else:
        print("Unknown command. Use 'ingest' or 'query <question>'.")
        sys.exit(1)
