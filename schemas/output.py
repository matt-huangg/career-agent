"""Pydantic models for structured agent output."""

from pydantic import BaseModel


class CareerInsight(BaseModel):
    """
    Structured output returned by the career agent.

    TODO:
    - Add or adjust fields as needed for your use case
    """
    summary: str
    strengths: list[str]
    gaps: list[str]
    recommendations: list[str]
    sources: list[str]
