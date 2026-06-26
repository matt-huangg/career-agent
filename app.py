"""Gradio chat UI for the Career Agent."""

from dotenv import load_dotenv
import gradio as gr

from schemas import CareerInsight

load_dotenv()


def format_insight(insight: CareerInsight) -> str:
    """
    Format a CareerInsight into a readable chat response.
    Returns a markdown string for display in the chat UI.
    """
    sections = [
        f"**Summary**\n{insight.summary}",
        "**Strengths**\n" + "\n".join(f"- {s}" for s in insight.strengths),
        "**Gaps**\n" + "\n".join(f"- {g}" for g in insight.gaps),
        "**Experiences**\n" + "\n".join(f"- {e}" for e in insight.experiences),
        "**Sources**\n" + "\n".join(f"- {s}" for s in insight.sources),
    ]
    return "\n\n".join(sections)


def chat(message: str, history: list) -> str:
    """
    Handle a user message and return the agent response for the chat UI.

    TODO:
    - Import and call run_agent(message) from agent.runner
    - Format the result with format_insight()
    - Return the formatted markdown string
    """
    _ = history  # Gradio passes chat history; may use for multi-turn later
    # TODO: replace placeholder once run_agent() is implemented
    return f"Agent not implemented yet. You asked: {message}"


def create_app() -> gr.Blocks:
    """
    Build and return the Gradio chat interface.

    TODO:
    - Customize theme, examples, or system instructions if needed
    - Add error handling for missing API key or empty knowledge base
    """
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
