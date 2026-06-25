"""Load raw personal data files from the data/ directory."""

from pathlib import Path


def load_documents(data_dir: str = "./data") -> list[dict]:
    """
    Walk the data directory and load supported file types.
    Returns a list of dicts with keys: source, content.
    Supported: .txt, .md, .json, .csv

    TODO:
    - Walk data_dir recursively for all supported file types
    - Read .txt and .md files as plain text
    - Parse .json files and serialize to a readable string
    - Parse .csv files row by row into a readable string
    - Return a list of {source, content} dicts
    """
    pass
