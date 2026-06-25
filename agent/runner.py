"""Agentic loop: retrieve context, call OpenAI, return structured output."""

from retrieval import retrieve
from schemas import CareerInsight

SYSTEM_PROMPT = """You are a personal career advisor with deep knowledge about the user.
You have access to the user's personal data including their resume, work history, skills, and goals.
Using the provided context, answer the query and return structured career insights.
Be specific, honest, and actionable."""


def run_agent(query: str, top_k: int = 5) -> CareerInsight:
    """
    Retrieve relevant context from the knowledge base and run the agent.
    Returns a structured CareerInsight.

    TODO:
    - Initialize OpenAI client
    - Call retrieve() to get the top_k relevant chunks for the query
    - Format chunks into a context string with source labels
    - Build the messages list with SYSTEM_PROMPT and user query + context
    - Call client.beta.chat.completions.parse() with response_format=CareerInsight
    - Attach sources to the result and return the parsed CareerInsight
    """
    pass
