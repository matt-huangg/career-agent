"""
Orchestrator — top-level router that directs queries to the right pipeline.

Routes:
  "chat"     → Chat Agent (ChromaDB retrieval only, fast, returns CareerInsight)
  "research" → Research pipeline (web search + quality review + format + email)
  "unknown"  → Query can't be answered — knowledge base has no relevant data

One asyncio.run() entry point here; all downstream agents are awaited directly.
"""

import asyncio

from agents import Agent, Runner, trace

from agent.orchestrator.schema import RouteDecision
from retrieval import retrieve

ORCHESTRATOR_INSTRUCTIONS = """
You are a routing agent for a personal career assistant.

You will receive a user query alongside the top matching chunks retrieved from the
user's personal knowledge base, including their similarity distance scores
(lower distance = more relevant).

Decide which pipeline should handle the query:

- "chat": the query is about the user's personal data and the retrieved chunks
  are relevant (low distance scores). Answer from stored profile data.
  Examples: "What are my strongest skills?", "What roles should I target?"

- "research": the query asks about the external world — industry trends, market
  demand, salary benchmarks. Requires live web research regardless of chunk relevance.
  Examples: "Is Python in demand right now?", "What are companies hiring for in AI?"

- "unknown": the retrieved chunks are not relevant to the query (high distances)
  and the question is clearly outside the scope of the user's career profile.
  Examples: "What's Matthew's favorite food?", "What is the capital of France?"

Return the route and a short reason explaining your decision.
"""


async def _classify(query: str) -> RouteDecision:
    """
    Retrieve top-k chunks and run the orchestrator agent to classify the query.
    Passing retrieved chunks gives the agent evidence to detect out-of-scope queries.
    """
    chunks = retrieve(query, top_k=5)
    context_block = "\n".join(
        f"[distance={c['distance']:.3f}] {c['content'][:200]}" for c in chunks
    )

    prompt = (
        f"User query: {query}\n\n"
        f"Top retrieved chunks from knowledge base:\n{context_block}"
    )

    router = Agent(
        name="Orchestrator",
        instructions=ORCHESTRATOR_INSTRUCTIONS,
        output_type=RouteDecision,
    )

    with trace("orchestrator-routing"):
        result = await Runner.run(router, input=prompt)

    return result.final_output


async def _run_pipeline(query: str) -> str:
    """
    Async pipeline — classifies the query then awaits the appropriate pipeline.
    All downstream agents are awaited directly; no nested asyncio.run() calls.
    """
    print(f"Routing query: {query!r}")
    decision = await _classify(query)
    print(f"  Route: {decision.route} ({decision.reason})")

    if decision.route == "chat":
        from agent.chat.runner import _run_chat

        insight = await _run_chat(query)
        return insight.response

    if decision.route == "research":
        from agent.formatter.runner import _run as _run_formatter
        from agent.mailer.runner import _run as _run_mailer
        from agent.research.runner import _run_research_pipeline

        report = await _run_research_pipeline()
        html = await _run_formatter(report)
        confirmation = await _run_mailer(html)
        return f"Research complete — {confirmation}"

    if decision.route == "unknown":
        return f"I don't have information about that in your profile data. ({decision.reason})"

    raise ValueError(f"Unexpected route: {decision.route}")


async def stream_pipeline(query: str):
    """
    Async generator — yields incremental status updates then the final response.
    Each yield is the full accumulated text so Gradio replaces the prior message.
    Used by the Gradio UI for a live streaming feel without token-level streaming.
    """
    # Show routing status immediately so the UI feels responsive
    text = "_Routing your query..._\n\n"
    yield text

    decision = await _classify(query)

    if decision.route == "chat":
        yield "_Searching your profile..._\n\n"

        from agent.chat.runner import stream_chat

        # Accumulate tokens and yield the growing text so Gradio re-renders each chunk
        accumulated = ""
        async for token in stream_chat(query):
            accumulated += token
            yield accumulated

    elif decision.route == "research":
        from agent.formatter.runner import _run as _run_formatter
        from agent.mailer.runner import _run as _run_mailer
        from agent.research.runner import _run_research_pipeline

        text = "_Searching the web for industry insights..._\n\n"
        yield text

        report = await _run_research_pipeline()
        # Append progress rather than replacing so the user sees the chain
        text += f"_Researched **{len(report.skills)} skills**. Formatting report..._\n\n"
        yield text

        html = await _run_formatter(report)
        text += "_Sending email..._\n\n"
        yield text

        confirmation = await _run_mailer(html)
        yield f"Research complete.\n\n{confirmation}"

    elif decision.route == "unknown":
        yield f"I don't have information about that in your profile data.\n\n_{decision.reason}_"

    else:
        raise ValueError(f"Unexpected route: {decision.route}")


def run_pipeline(query: str) -> str:
    """
    Sync entry point for app.py and main.py.
    Single asyncio.run() for the entire pipeline — no nested event loops.
    """
    return asyncio.run(_run_pipeline(query))


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    queries = [
        "What are my strongest skills?",
        "Is Python still in demand in the industry today?",
        "What is Matthew's favorite food?",
    ]

    for q in queries:
        print(f"\n--- Query: {q!r} ---")
        result = run_pipeline(q)
        print(f"Result: {result[:200]}")
