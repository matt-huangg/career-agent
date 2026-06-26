"""Formatter agent — converts a ResearchReport into a styled HTML email."""

import asyncio

from agents import Agent, Runner

from agent.research.schema import ResearchReport

FORMATTER_INSTRUCTIONS = """
You are an HTML email formatter. You receive a career skills research report as JSON
and convert it into a clean, professional HTML email.

Guidelines:
- Use simple, readable HTML with inline styles (no external CSS)
- Include a header, one section per skill with its demand level and summary
- End with an overall summary section
- Keep it professional and easy to scan
- Output only valid HTML, no markdown or explanation
"""


async def _run(report: ResearchReport) -> str:
    """Run the formatter agent and return the HTML string."""
    formatter = Agent(
        name="HTML Formatter",
        instructions=FORMATTER_INSTRUCTIONS,
        # no tools needed — pure LLM formatting task
    )

    result = await Runner.run(
        formatter,
        input=report.model_dump_json(indent=2),
    )

    return result.final_output


def run_formatter(report: ResearchReport) -> str:
    """
    Convert a ResearchReport into an HTML email string.
    Synchronous wrapper around the async agent runner.
    """
    return asyncio.run(_run(report))


if __name__ == "__main__":
    # Smoke test with a minimal report
    from agent.research.schema import SkillReport

    sample = ResearchReport(
        skills=[
            SkillReport(
                skill="Python",
                summary="Python remains one of the most in-demand languages in tech, "
                        "particularly for AI, data engineering, and backend services.",
                demand_level="High",
            )
        ],
        overall_summary="Strong alignment with current industry demand.",
    )

    html = run_formatter(sample)
    print(html[:500])
