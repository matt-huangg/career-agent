"""Split documents into chunks for embedding."""

CHUNK_SIZE = 500    # tokens
CHUNK_OVERLAP = 50  # tokens


def chunk_documents(documents: list[dict], model: str = "text-embedding-3-small") -> list[dict]:
    """
    Split each document into token-bounded chunks.
    Returns a list of dicts with keys: source, content, chunk_index.

    TODO:
    - Load the tiktoken encoder for the given model
    - For each document, encode the content into tokens
    - Slide a window of CHUNK_SIZE tokens with CHUNK_OVERLAP between chunks
    - Decode each window back to text
    - Return a list of {source, content, chunk_index} dicts
    """
    pass
