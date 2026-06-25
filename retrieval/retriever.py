"""Query ChromaDB with an embedded query and return top-k chunks."""

COLLECTION_NAME = "career_knowledge"


def retrieve(query: str, top_k: int = 5) -> list[dict]:
    """
    Embed the query and return the top_k most relevant chunks from ChromaDB.
    Returns a list of dicts with keys: content, source, distance.

    TODO:
    - Initialize OpenAI client and ChromaDB PersistentClient
    - Embed the query string using the OpenAI embeddings API
    - Query the ChromaDB collection with the query embedding
    - Unpack results (documents, metadatas, distances) into a list of dicts
    - Return the list
    """
    pass
