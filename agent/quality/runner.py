"""Quality agent — reviews a ResearchReport and approves or requests improvements."""

import asyncio

from agents import Agent, Runner

from agent.quality.schema import QualityVerdict
from agent.research.schema import ResearchReport

QUALITY_INSTRUCTIONS = """
You are a quality reviewer for career research reports.
Review the provided ResearchReport JSON against these criteria:

- At least 3 skills must be present
- Each skill must have a substantive summary of at least 2 paragraphs (not vague or generic)
- demand_level must be one of: "High", "Growing", "Moderate", or "Niche"
- overall_summary must be specific to this person's skill set, not generic career advice

If the report meets all criteria, set approved=True and feedback="".
If not, set approved=False and explain specifically what needs to be improved in feedback.
"""


async def _run(report: ResearchReport) -> QualityVerdict:
    """Run the quality agent against a ResearchReport."""
    reviewer = Agent(
        name="Quality Reviewer",
        instructions=QUALITY_INSTRUCTIONS,
        output_type=QualityVerdict,
        # no tools — pure LLM judgment
    )

    result = await Runner.run(
        reviewer,
        input=report.model_dump_json(indent=2),
    )

    return result.final_output


def review_report(report: ResearchReport) -> QualityVerdict:
    """
    Review a ResearchReport and return a QualityVerdict.
    Synchronous wrapper around the async quality agent.
    """
    return asyncio.run(_run(report))
