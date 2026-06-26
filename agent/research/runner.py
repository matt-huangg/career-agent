"""Research agent — retrieves skills from ChromaDB and researches industry relevance."""

import asyncio

from agents import Agent, Runner, WebSearchTool, trace

from agent.research.schema import ResearchReport
from retrieval import retrieve

MAX_RETRIES = 3  # cap retries to avoid runaway API costs

RESEARCH_INSTRUCTIONS = """
You are a career research analyst. You will be given a list of skills extracted from
a person's career profile. For each skill:

1. Search the web for its current industry demand and relevance in tech
2. Write a 2-3 paragraph summary covering:
   - How widely used and in-demand the skill is right now
   - Which industries or roles value it most
   - Where it's heading (growing, stable, declining)
3. Assign a demand_level: one of "High", "Growing", "Moderate", or "Niche"

Be specific and cite real trends, not generic statements.
Then write an overall_summary tying the skill set together.
"""


async def _run_once(skills_context: str, feedback: str | None = None) -> ResearchReport:
    """Run one attempt of the research agent."""
    prompt = f"Research the industry relevance of these skills:\n\n{skills_context}"

    # Append quality feedback on retries so the agent knows what to improve
    if feedback:
        prompt += f"\n\nPrevious attempt was rejected. Please improve on: {feedback}"

    researcher = Agent(
        name="Career Research Agent",
        instructions=RESEARCH_INSTRUCTIONS,
        tools=[WebSearchTool(search_context_size="medium")],
        output_type=ResearchReport,
    )

    result = await Runner.run(researcher, input=prompt)
    return result.final_output


async def _run_research_pipeline() -> ResearchReport:
    """
    Async entry point — called directly by the orchestrator.
    Retrieves skills from ChromaDB and runs the quality loop.
    """
    chunks = retrieve("top skills strengths technical expertise frameworks tools", top_k=8)
    skills_context = "\n\n".join(
        f"[Source: {c['source']}]\n{c['content']}" for c in chunks
    )
    return await _run_with_quality_loop(skills_context)


async def _run_with_quality_loop(skills_context: str) -> ResearchReport:
    """
    Run the research agent with a quality review loop.
    Retries up to MAX_RETRIES times if the quality agent rejects the report.
    Imports quality reviewer here to avoid circular imports.
    """
    # Lazy import — quality imports research schema; research must not import quality at top-level
    # Import the async _run directly so we can await it — calling the sync wrapper
    # review_report() would try asyncio.run() inside a running loop, which fails.
    from agent.quality.runner import _run as quality_run

    feedback: str | None = None

    for attempt in range(1, MAX_RETRIES + 1):
        print(f"  [Research attempt {attempt}/{MAX_RETRIES}]")

        with trace(f"research-agent attempt={attempt}"):
            report = await _run_once(skills_context, feedback=feedback)

        verdict = await quality_run(report)

        if verdict.approved:
            print("  Quality approved.")
            return report

        feedback = verdict.feedback
        print(f"  Quality rejected: {feedback}")

    # Return best effort after max retries
    print("  Max retries reached — returning last report.")
    return report


def run_research() -> ResearchReport:
    """
    Sync entry point for standalone testing.
    Do not call from inside an async context — use _run_research_pipeline() instead.
    """
    return asyncio.run(_run_research_pipeline())


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    print("Running research agent with quality loop...")
    report = run_research()
    print(f"\nResearched {len(report.skills)} skills\n")
    for skill in report.skills:
        print(f"  [{skill.demand_level}] {skill.skill}")
        print(f"    {skill.summary[:120]}...")
    print(f"\nOverall: {report.overall_summary[:200]}")
