"""Mailer agent — receives HTML content and sends it via the send_email tool."""

import asyncio

from agents import Agent, Runner

from agent.mailer.tools import send_email

MAILER_INSTRUCTIONS = """
You are an email delivery agent. You receive an HTML email body and must send it
using the send_email tool with an appropriate subject line.

- Generate a concise, professional subject line based on the content
- Call send_email exactly once with the subject and the full HTML body provided
- Report back what the tool returned
"""


async def _run(html_body: str) -> str:
    """Run the mailer agent and return the delivery confirmation."""
    mailer = Agent(
        name="Mailer Agent",
        instructions=MAILER_INSTRUCTIONS,
        tools=[send_email],  # the agent decides when to call this
    )

    result = await Runner.run(
        mailer,
        input=f"Send this HTML email:\n\n{html_body}",
    )

    return result.final_output


def run_mailer(html_body: str) -> str:
    """
    Deliver an HTML email via the mailer agent.
    Synchronous wrapper around the async agent runner.
    """
    return asyncio.run(_run(html_body))
