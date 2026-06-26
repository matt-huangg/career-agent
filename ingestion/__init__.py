"""Ingestion pipeline: load, chunk, and embed personal data."""

from .chunker import chunk_documents
from .embedder import embed_and_store
from .loader import load_documents

__all__ = ["load_documents", "chunk_documents", "embed_and_store"]
