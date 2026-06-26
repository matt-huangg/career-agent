"""Schema for the orchestrator's routing decision."""

from typing import Literal

from pydantic import BaseModel


class RouteDecision(BaseModel):
    """Decision returned by the orchestrator on how to handle a user query."""

    route: Literal["chat", "research", "unknown"]  # which pipeline to invoke
    reason: str                                    # why this route was chosen
