"""Gradio chat UI for the Career Agent."""

from dotenv import load_dotenv
import gradio as gr

from agent.orchestrator import stream_pipeline

load_dotenv()


async def chat(message: str, history: list):
    """
    Async generator — streams status updates and the final response to Gradio.
    Each yield replaces the previous message in the chat UI.
    """
    _ = history  # Gradio passes chat history; may use for multi-turn later
    try:
        async for chunk in stream_pipeline(message):
            yield chunk
    except Exception as exc:
        yield f"**Error**\n\n{exc}"


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
            "Is Python still in demand in industry today?",
        ],
    )


if __name__ == "__main__":
    create_app().launch()
