"""Pydantic models for structured agent output."""

from pydantic import BaseModel


class CareerInsight(BaseModel):
    """
    Structured output returned by the career agent.
    """
    response: str
  
