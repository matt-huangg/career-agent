"""Split documents into chunks for embedding."""

import tiktoken
from langchain_text_splitters import RecursiveCharacterTextSplitter

CHUNK_SIZE = 500    # tokens
CHUNK_OVERLAP = 50  # tokens — repeated at start of each chunk to avoid cutting mid-thought


def chunk_documents(documents: list[dict], model: str = "text-embedding-3-small") -> list[dict]:
    """
    Split each document into token-bounded chunks using semantic boundaries.
    Returns a list of dicts with keys: source, content, chunk_index.
    """
    # tiktoken converts text → token IDs so we can count tokens, not characters
    encoder = tiktoken.encoding_for_model(model)

    # RecursiveCharacterTextSplitter tries to split on paragraph breaks → line breaks
    # → spaces → characters, preferring the largest natural boundary it can find.
    # length_function swaps the default character counter for a token counter.
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=lambda text: len(encoder.encode(text)),
    )

    chunks = []
    for doc in documents:
        # split_text returns a list of strings, each within the token limit
        texts = splitter.split_text(doc["content"])
        for i, text in enumerate(texts):
            chunks.append({
                "source": doc["source"],   # preserve origin file for citations
                "content": text,
                "chunk_index": i,          # position within the original document
            })

    return chunks


if __name__ == "__main__":
    from ingestion.loader import load_documents

    docs = load_documents()
    chunks = chunk_documents(docs)
    print(f"{len(docs)} documents -> {len(chunks)} chunks")

    by_source: dict[str, int] = {}
    for chunk in chunks:
        by_source[chunk["source"]] = by_source.get(chunk["source"], 0) + 1

    for source, count in sorted(by_source.items(), key=lambda x: -x[1]):
        print(f"  {count:4d} chunks  {source}")
