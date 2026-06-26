# Career Agent

A Python AI agent that ingests your personal career data, indexes it for semantic search (RAG), and returns structured career insights — powered by the OpenAI SDK.

## Overview

Career Agent is a personal AI assistant designed to reason about your career. It loads data about you (resume exports, LinkedIn CSVs, goals, work history), chunks and embeds it into a local vector store, and uses retrieval-augmented generation to answer questions with structured, cited output.

## Features

- **Personal data ingestion** — load JSON and CSV files from `data/` (including nested directories)
- **RAG pipeline** — semantic chunking (LangChain), OpenAI embeddings, and ChromaDB for local vector search
- **Agentic reasoning** — retrieve context and generate answers via the OpenAI SDK *(in progress)*
- **Structured output** — typed responses validated with Pydantic (`CareerInsight`)
- **Gradio chat UI** — interactive web chat to query the agent *(scaffolded)*

## Tech Stack

- **Language:** Python 3.11+
- **Package manager:** [uv](https://docs.astral.sh/uv/)
- **AI SDK:** OpenAI Python SDK
- **Vector store:** ChromaDB (local, `./chroma_db`)
- **Embeddings:** OpenAI `text-embedding-3-small`
- **Chunking:** LangChain `RecursiveCharacterTextSplitter` + tiktoken
- **Structured output:** Pydantic models
- **UI (planned):** Gradio

## Project Structure

```
career-agent/
├── data/               # Personal data files (gitignored) — JSON, CSV
├── chroma_db/          # Local ChromaDB store (gitignored)
├── ingestion/
│   ├── loader.py       # Walk data/ and load JSON + CSV files
│   ├── chunker.py      # Split documents into token-bounded chunks
│   └── embedder.py     # Embed chunks and upsert into ChromaDB
├── retrieval/
│   └── retriever.py    # Query ChromaDB for relevant chunks
├── agent/
│   └── runner.py       # RAG + OpenAI agent loop
├── schemas/
│   └── output.py       # CareerInsight Pydantic model
├── app.py              # Gradio chat UI
├── main.py             # CLI entry point (ingest / query)
└── pyproject.toml      # Dependencies (managed with uv)
```

## Getting Started

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- OpenAI API key

### Installation

```bash
git clone <repo-url>
cd career-agent
uv sync
```

### Configuration

```bash
cp .env.example .env
# Add your OPENAI_API_KEY to .env
```

Required environment variables:

| Variable | Description |
|---|---|
| `OPENAI_API_KEY` | Your OpenAI API key |
| `OPENAI_EMBEDDING_MODEL` | Embedding model (default: `text-embedding-3-small`) |
| `OPENAI_CHAT_MODEL` | Chat model for the agent (default: `gpt-4o`) |
| `CHROMA_DB_PATH` | Local ChromaDB path (default: `./chroma_db`) |

### Add Your Data

Place personal files in `data/`. Supported formats:

- `.json` — career profiles, exports
- `.csv` — LinkedIn exports, spreadsheets

Files in subdirectories are picked up automatically (e.g. `data/linkedin-export/Profile.csv`).

## Usage

### 1. Ingest — index your data

Run the full pipeline: load → chunk → embed → store in ChromaDB.

```bash
uv run python main.py ingest
```

Or run each step individually for testing:

```bash
uv run python -m ingestion.loader    # load files from data/
uv run python -m ingestion.chunker    # split into chunks
uv run python ingestion/embedder.py   # embed and store in ChromaDB
```

Ingestion only needs to run once, or again when your data changes.

### 2. Query — ask the agent (CLI)

```bash
uv run python main.py query "What are my strongest skills?"
```

Returns a structured `CareerInsight` with summary, strengths, gaps, experiences, and sources.

### 3. Chat — Gradio UI

Launch the web chat (scaffolded — returns a placeholder until the agent is wired up):

```bash
uv run python app.py
```

Opens a local Gradio interface in your browser.

## Development

Each pipeline module can be tested standalone:

```bash
uv run python -m ingestion.loader
uv run python -m ingestion.chunker
uv run python ingestion/embedder.py
```

Use `uv run` for all commands — it runs inside the project virtualenv without manual activation.

## Roadmap

- [x] Data loader (JSON + CSV)
- [x] Semantic chunking with LangChain
- [x] OpenAI embeddings + ChromaDB storage
- [ ] Retriever
- [ ] Agent loop + structured output
- [ ] Wire up `main.py` ingest / query commands
- [ ] Wire Gradio chat to `run_agent()`
