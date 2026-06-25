# Career Agent

A Python AI agentic system that ingests personal data about you, retrieves relevant context via RAG (Retrieval-Augmented Generation), and returns structured output — powered by the OpenAI SDK.

## Overview

Career Agent is a personal AI assistant designed to reason about your career. It ingests data sources about you (resume, work history, skills, goals, etc.), indexes them for semantic retrieval, and uses an agentic loop to answer queries and generate structured career insights.

## Features

- **Personal data ingestion** — load and parse documents about yourself (resume, bios, notes, etc.)
- **RAG pipeline** — chunk, embed, and retrieve relevant context from your personal data
- **Agentic reasoning** — multi-step agent loop using the OpenAI SDK
- **Structured output** — responses returned as typed, schema-validated objects

## Tech Stack

- **Language:** Python
- **AI SDK:** OpenAI Python SDK
- **Vector store:** ChromaDB (local)
- **RAG:** OpenAI embeddings + ChromaDB for semantic search over personal data
- **Structured output:** OpenAI structured outputs / Pydantic models

## Project Structure

```
career-agent/
├── data/               # Raw personal data files (resume, notes, etc.)
├── ingestion/          # Data loading, chunking, and embedding pipeline
├── retrieval/          # Vector store and RAG query logic
├── agent/              # Agentic loop and tool definitions
├── schemas/            # Pydantic models for structured output
├── main.py             # Entry point
└── requirements.txt    # Python dependencies
```

## Getting Started

### Prerequisites

- Python 3.11+
- OpenAI API key
- ChromaDB runs locally — no external services needed

### Installation

```bash
git clone <repo-url>
cd career-agent
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Configuration

```bash
cp .env.example .env
# Add your OPENAI_API_KEY to .env
```

### Run

```bash
python main.py
```

## Usage

1. Add your personal documents to the `data/` directory
2. Run the ingestion pipeline to embed and index your data
3. Query the agent — it will retrieve relevant context from your data and return structured career insights
