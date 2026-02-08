"""
Feedback Handler Agent for the Banking Customer Support
Multi-Agent System.
"""

from utils.logger import log_event
from database.db import insert_ticket


# ------------------------------------------------------------------
# POSITIVE FEEDBACK
# ------------------------------------------------------------------

def handle_positive_feedback(user_message: str, customer_name: str) -> str:
    response = (
        f"Thank you for your kind words, {customer_name}! "
        "We’re delighted to assist you."
    )

    log_event(
        agent="FeedbackHandlerAgent",
        input_text=user_message,
        output_text="Positive feedback acknowledged"
    )

    return response


# ------------------------------------------------------------------
# NEGATIVE FEEDBACK
# ------------------------------------------------------------------

def handle_negative_feedback(user_message: str, customer_name: str) -> str:
    ticket_number = insert_ticket(
        issue_description=user_message,
        status="Open"
    )

    response = (
        "We apologize for the inconvenience. "
        f"A new ticket #{ticket_number} has been generated, "
        "and our team will follow up shortly."
    )

    log_event(
        agent="FeedbackHandlerAgent",
        input_text=user_message,
        output_text=f"Negative feedback logged with ticket #{ticket_number}"
    )

    return response
