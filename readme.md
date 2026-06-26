# Career Agent

A multi-agent AI system that ingests your personal career data, indexes it for semantic search (RAG), and routes queries to the right pipeline — either answering from your stored profile or launching a live web research report emailed directly to you.

## Overview

Career Agent is a personal AI assistant designed to reason about your career. It loads data about you (resume exports, LinkedIn CSVs, goals, work history), chunks and embeds it into a local vector store, and uses an orchestrator agent to decide how to handle each query:

- **Chat queries** (e.g. "What are my strongest skills?") → retrieved from ChromaDB and answered via the OpenAI SDK
- **Research queries** (e.g. "Is Python still in demand?") → web-researched by a multi-agent pipeline, quality-reviewed, formatted as HTML, and emailed to you

## Features

- **Personal data ingestion** — load JSON and CSV files from `data/` (including nested directories)
- **RAG pipeline** — semantic chunking (LangChain), OpenAI embeddings, ChromaDB local vector search
- **Orchestrator routing** — classifies each query as `chat`, `research`, or `unknown` before dispatching
- **Deep research pipeline** — web search agent → quality review loop → HTML formatter → email delivery
- **Quality review loop** — research reports are automatically reviewed and retried (up to 3×) until approved
- **Structured output** — all agent responses are typed Pydantic models (`CareerInsight`, `ResearchReport`, `RouteDecision`)
- **Gradio chat UI** — interactive web chat wired to the full orchestrator pipeline
- **Smart data filtering** — LinkedIn messages filtered to exclude sponsored conversations and messages older than 365 days

## Tech Stack

| Layer | Tool |
|---|---|
| Language | Python 3.11+ |
| Package manager | [uv](https://docs.astral.sh/uv/) |
| AI agents | [OpenAI Agents SDK](https://github.com/openai/openai-agents-python) (`openai-agents`) |
| LLM / embeddings | OpenAI (`gpt-4o`, `text-embedding-3-small`) |
| Vector store | ChromaDB (local, `./chroma_db`) |
| Chunking | LangChain `RecursiveCharacterTextSplitter` + tiktoken |
| Structured output | Pydantic v2 |
| Email delivery | SendGrid |
| UI | Gradio |

## Project Structure

```
career-agent/
├── data/                   # Personal data files (gitignored) — JSON, CSV
├── chroma_db/              # Local ChromaDB store (gitignored)
│
├── ingestion/
│   ├── loader.py           # Walk data/ and parse JSON + CSV files
│   ├── chunker.py          # Split documents into token-bounded chunks
│   └── embedder.py         # Embed chunks and upsert into ChromaDB
│
├── retrieval/
│   └── retriever.py        # Query ChromaDB for semantically relevant chunks
│
├── agent/
│   ├── orchestrator/       # Top-level router — classifies queries and runs the pipeline
│   │   ├── runner.py       # route_query() + run_pipeline() — single asyncio.run() entry
│   │   └── schema.py       # RouteDecision model (route, reason)
│   │
│   ├── chat/               # Answers profile questions from ChromaDB context
│   │   ├── runner.py       # _run_chat() / run_agent()
│   │   └── schema.py       # CareerInsight model
│   │
│   ├── research/           # Web research agent with quality review loop
│   │   ├── runner.py       # _run_research_pipeline() / run_research()
│   │   └── schema.py       # ResearchReport + SkillReport models
│   │
│   ├── quality/            # Reviews research reports and approves or requests retry
│   │   ├── runner.py       # review_report() / _run()
│   │   └── schema.py       # QualityVerdict model (approved, feedback)
│   │
│   ├── formatter/          # Converts ResearchReport JSON → styled HTML email
│   │   └── runner.py       # run_formatter() / _run()
│   │
│   └── mailer/             # Sends the HTML email via SendGrid
│       ├── runner.py       # run_mailer() / _run()
│       └── tools.py        # send_email() function tool
│
├── app.py                  # Gradio chat UI
├── main.py                 # CLI entry point (ingest / query)
└── pyproject.toml          # Dependencies (managed with uv)
```

## Agent Pipeline

```
User query
  └─ Orchestrator (classifies route)
       ├─ "chat"      → Chat Agent → CareerInsight (from ChromaDB)
       ├─ "research"  → Research Agent (WebSearchTool)
       │                  └─ Quality Reviewer (retry loop, up to 3×)
       │                       └─ HTML Formatter
       │                            └─ Mailer Agent (SendGrid)
       └─ "unknown"  → "I don't have information about that"
```

## Getting Started

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- OpenAI API key
- SendGrid API key (for the research email pipeline)

### Installation

```bash
git clone <repo-url>
cd career-agent
uv sync
```

### Configuration

```bash
cp .env.example .env
# Fill in your API keys
```

Required environment variables:

| Variable | Description |
|---|---|
| `OPENAI_API_KEY` | Your OpenAI API key |
| `SENDGRID_API_KEY` | Your SendGrid API key (research pipeline only) |
| `SENDGRID_FROM_EMAIL` | Verified sender address in SendGrid |
| `SENDGRID_TO_EMAIL` | Recipient address for research reports |
| `OPENAI_EMBEDDING_MODEL` | Embedding model (default: `text-embedding-3-small`) |
| `OPENAI_CHAT_MODEL` | Chat model (default: `gpt-4o`) |
| `CHROMA_DB_PATH` | Local ChromaDB path (default: `./chroma_db`) |

### Add Your Data

Place personal files in `data/`. Supported formats:

- `.json` — career profiles, exports
- `.csv` — LinkedIn exports (Profile, Positions, Skills, Messages, etc.)

Files in subdirectories are picked up automatically (e.g. `data/linkedin-export/Profile.csv`).

## Usage

### 1. Ingest — index your data

Run the full pipeline: load → chunk → embed → store in ChromaDB.

```bash
uv run python main.py ingest
```

Or test each step individually:

```bash
uv run python -m ingestion.loader     # load and parse files from data/
uv run python -m ingestion.chunker    # split into token-bounded chunks
uv run python -m ingestion.embedder   # embed and store in ChromaDB
```

Ingestion only needs to run once, or again when your data changes.

### 2. Chat — Gradio UI

```bash
uv run python app.py
```

Opens a local Gradio interface at `http://localhost:7860`. Example queries:

- `"What are my strongest skills?"` → answered from your profile (chat route)
- `"Is Python still in demand in industry?"` → researched on the web and emailed (research route)

### 3. Test individual agents

Each agent module has a standalone test block:

```bash
uv run python -m agent.research.runner     # run research pipeline + quality loop
uv run python -m agent.formatter.runner    # format a sample ResearchReport as HTML
uv run python -m agent.orchestrator.runner # test all three routes
```

## Async Architecture

All agent runners are fully async end-to-end. The orchestrator's `run_pipeline()` is the single `asyncio.run()` entry point — everything below it is `await`ed directly, avoiding nested event loop errors.

```
asyncio.run(run_pipeline())         ← one event loop, started here
  └─ await _run_pipeline()
       ├─ await _classify()
       ├─ await _run_chat()
       └─ await _run_research_pipeline()
            ├─ await _run_with_quality_loop()
            ├─ await _run_formatter()
            └─ await _run_mailer()
```

## Roadmap

- [x] Data loader (JSON + CSV) with LinkedIn message filtering
- [x] Semantic chunking with LangChain + tiktoken
- [x] OpenAI embeddings + ChromaDB storage
- [x] Retriever — semantic search over ChromaDB
- [x] Orchestrator — routes queries to chat or research pipeline
- [x] Chat agent — structured `CareerInsight` output from ChromaDB context
- [x] Research agent — web search via `WebSearchTool` + Pydantic `ResearchReport`
- [x] Quality review loop — auto-retry with feedback up to 3×
- [x] HTML formatter agent — converts report to styled email
- [x] Mailer agent — delivers report via SendGrid
- [x] Gradio chat UI wired to orchestrator
- [ ] Multi-turn conversation support in Gradio
- [ ] Wire up `main.py` ingest / query CLI commands
- [ ] Persist conversation history across sessions
