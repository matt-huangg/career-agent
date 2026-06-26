"""Embed chunks and store them in ChromaDB."""

import os

import chromadb
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

COLLECTION_NAME = "career_knowledge"
CHROMA_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")        # local on-disk store — gitignored
EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
BATCH_SIZE = 100  # OpenAI accepts many inputs per call; batch to stay within limits


def embed_and_store(chunks: list[dict]) -> None:
    """
    Embed each chunk with OpenAI and upsert into local ChromaDB.
    Expects chunks with keys: source, content, chunk_index.
    """
    if not chunks:
        return

    # OpenAI reads OPENAI_API_KEY from the environment
    client = OpenAI()
    chroma = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = chroma.get_or_create_collection(name=COLLECTION_NAME)

    for start in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[start : start + BATCH_SIZE]

        texts = [chunk["content"] for chunk in batch]
        ids = [f"{chunk['source']}::{chunk['chunk_index']}" for chunk in batch]
        metadatas = [
            {"source": chunk["source"], "chunk_index": chunk["chunk_index"]}
            for chunk in batch
        ]

        # Convert text → vectors via OpenAI embeddings API
        response = client.embeddings.create(model=EMBEDDING_MODEL, input=texts)
        embeddings = [item.embedding for item in response.data]

        # Upsert so re-running ingest updates existing chunks instead of duplicating
        collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
        )


if __name__ == "__main__":
    try:
        from .chunker import chunk_documents
        from .loader import load_documents
    except ImportError:
        # Running as `python ingestion/embedder.py` — add project root to import path
        import sys
        from pathlib import Path

        sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
        from ingestion.chunker import chunk_documents
        from ingestion.loader import load_documents

    load_dotenv()

    docs = load_documents()
    chunks = chunk_documents(docs)
    embed_and_store(chunks)

    chroma = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = chroma.get_collection(name=COLLECTION_NAME)
    print(f"Stored {len(chunks)} chunks in '{COLLECTION_NAME}' ({collection.count()} total in DB)")
