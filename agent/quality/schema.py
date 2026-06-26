"""Schema for the quality agent's verdict on a ResearchReport."""

from pydantic import BaseModel


class QualityVerdict(BaseModel):
    """Decision returned by the quality agent after reviewing a ResearchReport."""

    approved: bool  # True = report meets quality bar, proceed to formatter
    feedback: str   # what to improve if rejected; empty string if approved
