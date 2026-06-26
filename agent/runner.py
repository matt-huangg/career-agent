"""Agentic loop: retrieve context, call OpenAI, return structured output."""

import os

from dotenv import load_dotenv
from openai import OpenAI

from retrieval import retrieve
from schemas import CareerInsight

load_dotenv()

CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o")

SYSTEM_PROMPT = """You are a personal career advisor with deep knowledge about the user.
You have access to the user's personal data including their resume, work history, skills, and goals.
Using the provided context, answer the query and return structured career insights.
Be specific, honest, and actionable. Only use information supported by the context."""


def _format_context(chunks: list[dict]) -> str:
    """Turn retrieved chunks into a labeled context block for the LLM prompt."""
    sections = []
    for i, chunk in enumerate(chunks, start=1):
        sections.append(
            f"[Context {i} | Source: {chunk['source']}]\n{chunk['content']}"
        )
    return "\n\n".join(sections)


def run_agent(query: str, top_k: int = 5) -> CareerInsight:
    """
    Retrieve relevant context from the knowledge base and run the agent.
    Returns a structured CareerInsight with sources from retrieved chunks.
    """
    client = OpenAI()
    chunks = retrieve(query, top_k=top_k)
    context = _format_context(chunks)

    user_message = (
        f"Context from the user's personal data:\n\n{context}\n\n"
        f"Question: {query}"
    )

    # Structured output ensures the response matches the CareerInsight schema
    completion = client.beta.chat.completions.parse(
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

    # Attach retrieval sources so citations reflect what was actually searched
    sources = list(dict.fromkeys(chunk["source"] for chunk in chunks))
    return insight.model_copy(update={"sources": sources})
