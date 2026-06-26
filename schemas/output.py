"""Pydantic models for structured agent output."""

from pydantic import BaseModel


class CareerInsight(BaseModel):
    """
    Structured output returned by the career agent.
    """
    summary: str
    strengths: list[str]
    gaps: list[str]
    experiences: list[str]
    sources: list[str]
