"""Embed chunks and store them in ChromaDB."""

COLLECTION_NAME = "career_knowledge"


def embed_and_store(chunks: list[dict]) -> None:
    """
    Embed each chunk with OpenAI and upsert into local ChromaDB.

    TODO:
    - Initialize OpenAI client and ChromaDB PersistentClient
    - Get or create the ChromaDB collection
    - Extract texts, ids, and metadatas from chunks
    - Call OpenAI embeddings API with the texts
    - Upsert embeddings, documents, and metadatas into ChromaDB
    """
    pass
