"""Gradio chat UI for the Career Agent."""

from dotenv import load_dotenv
import gradio as gr

from agent import run_agent
from schemas import CareerInsight

load_dotenv()


def format_insight(insight: CareerInsight) -> str:
    """
    Format a CareerInsight into a readable chat response.
    Returns a markdown string for display in the chat UI.
    """
    sections = [
        f"{insight.response}",
    ]
    return "\n\n".join(sections)


def chat(message: str, history: list) -> str:
    """
    Handle a user message and return the agent response for the chat UI.
    Retrieves context from ChromaDB and returns a formatted CareerInsight.
    """
    _ = history  # Gradio passes chat history; may use for multi-turn later
    try:
        insight = run_agent(message)
        return format_insight(insight)
    except Exception as exc:
        return f"**Error**\n\n{exc}"


def create_app() -> gr.Blocks:
    """Build and return the Gradio chat interface."""
    return gr.ChatInterface(
        fn=chat,
        title="Career Agent",
        description="Ask questions about your career. Answers are grounded in your indexed personal data.",
        examples=[
            "What are my strongest skills?",
            "What roles should I target next?",
            "What gaps should I work on?",
        ],
    )


if __name__ == "__main__":
    create_app().launch()
