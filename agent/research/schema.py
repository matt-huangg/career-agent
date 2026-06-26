"""Pydantic schemas for the research agent's structured output."""

from pydantic import BaseModel


class SkillReport(BaseModel):
    """Industry relevance report for a single skill."""

    skill: str
    summary: str        # 2-3 paragraphs on industry relevance
    demand_level: str   # e.g. "High", "Growing", "Niche"


class ResearchReport(BaseModel):
    """Full research report returned by the research agent."""

    skills: list[SkillReport]
    overall_summary: str
