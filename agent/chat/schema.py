"""Pydantic schema for the chat agent's structured output."""

from pydantic import BaseModel


class CareerInsight(BaseModel):
    """Structured output returned by the chat agent."""

    response: str
