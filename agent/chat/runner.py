"""Agentic loop: retrieve context, call OpenAI, return structured or streamed output."""

import asyncio
import os
from typing import AsyncIterator

from dotenv import load_dotenv
from openai import AsyncOpenAI, OpenAI

from retrieval import retrieve
from agent.chat.schema import CareerInsight

load_dotenv()

CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o")

SYSTEM_PROMPT = """You are a personal career advisor with deep knowledge about the user.
You have access to the user's personal data including their resume, work history, skills, and goals.
Using the provided context, answer the query in clear markdown.
Be specific, honest, and actionable. Only use information supported by the context."""


def _format_context(chunks: list[dict]) -> str:
    """Turn retrieved chunks into a labeled context block for the LLM prompt."""
    sections = []
    for i, chunk in enumerate(chunks, start=1):
        sections.append(
            f"[Context {i} | Source: {chunk['source']}]\n{chunk['content']}"
        )
    return "\n\n".join(sections)


def _build_user_message(query: str, chunks: list[dict]) -> str:
    """Assemble the full user prompt from retrieved context and the query."""
    context = _format_context(chunks)
    return (
        f"Context from the user's personal data:\n\n{context}\n\n"
        f"Question: {query}"
    )


async def stream_chat(query: str, top_k: int = 5) -> AsyncIterator[str]:
    """
    Async generator — streams response tokens one chunk at a time.
    Uses AsyncOpenAI with stream=True; yields raw text deltas as they arrive.
    Called by stream_pipeline in the orchestrator for live token streaming.
    """
    client = AsyncOpenAI()
    chunks = retrieve(query, top_k=top_k)
    user_message = _build_user_message(query, chunks)

    # stream=True makes the API return an async iterable of SSE events
    stream = await client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        stream=True,
    )

    async for event in stream:
        delta = event.choices[0].delta.content
        if delta:  # None on the final chunk
            yield delta


async def _run_chat(query: str, top_k: int = 5) -> CareerInsight:
    """
    Async entry point for non-streaming use — collects the full response
    via structured output and returns a CareerInsight object.
    Used when programmatic access to the parsed schema is needed.
    """
    client = AsyncOpenAI()
    chunks = retrieve(query, top_k=top_k)
    user_message = _build_user_message(query, chunks)

    # parse() enforces the CareerInsight schema via structured output
    completion = await client.beta.chat.completions.parse(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        response_format=CareerInsight,
    )

    insight = completion.choices[0].message.parsed
    if insight is None:
        raise ValueError("Model returned no parsed CareerInsight")
    return insight


def run_agent(query: str, top_k: int = 5) -> CareerInsight:
    """
    Sync entry point for standalone CLI use.
    Do not call from inside an async context — use _run_chat() instead.
    """
    return asyncio.run(_run_chat(query, top_k))
