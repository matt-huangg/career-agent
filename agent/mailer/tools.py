"""SendGrid email tool for the mailer agent."""

import os

from agents import function_tool
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


@function_tool
def send_email(subject: str, html_body: str) -> str:
    """
    Send an HTML email via SendGrid.
    Reads SENDGRID_API_KEY, REPORT_FROM_EMAIL, and REPORT_TO_EMAIL from the environment.
    Returns a confirmation string with the HTTP status code.
    """
    api_key = os.environ["SENDGRID_API_KEY"]
    from_email = os.environ["REPORT_FROM_EMAIL"]
    to_email = os.environ["REPORT_TO_EMAIL"]

    message = Mail(
        from_email=from_email,
        to_emails=to_email,
        subject=subject,
        html_content=html_body,
    )

    client = SendGridAPIClient(api_key)
    response = client.send(message)

    # 202 means SendGrid accepted the email for delivery
    return f"Email sent — status {response.status_code} to {to_email}"
