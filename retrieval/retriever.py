"""Query ChromaDB with an embedded query and return top-k chunks."""

import os

import chromadb
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

COLLECTION_NAME = "career_knowledge"
CHROMA_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")


def retrieve(query: str, top_k: int = 5) -> list[dict]:
    """
    Embed the query and return the top_k most relevant chunks from ChromaDB.
    Returns a list of dicts with keys: content, source, distance.
    """
    client = OpenAI()
    chroma = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = chroma.get_collection(name=COLLECTION_NAME)

    # Embed the query using the same model used during ingest so vectors are comparable
    embedded_query = client.embeddings.create(model=EMBEDDING_MODEL, input=[query])
    query_vector = embedded_query.data[0].embedding

    # ChromaDB returns results sorted by similarity (closest first)
    results = collection.query(
        query_embeddings=[query_vector],   # list because ChromaDB supports batch queries
        n_results=top_k,                   # how many chunks to return
        include=["documents", "metadatas", "distances"],  # omit to get only IDs
    )

    # Unpack the nested lists ChromaDB returns (one list per query embedding)
    chunks = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        chunks.append({
            "content": doc,
            "source": meta["source"],  # original file path preserved from ingest
            "distance": dist,          # lower = more similar
        })

    return chunks


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    test_query = "What are my strongest skills?"
    chunks = retrieve(test_query, top_k=3)

    print(f"Top {len(chunks)} chunks for: '{test_query}'\n")
    for i, chunk in enumerate(chunks):
        print(f"[{i+1}] source: {chunk['source']}  distance: {chunk['distance']:.4f}")
        print(f"    {chunk['content'][:120]}...")
        print()
