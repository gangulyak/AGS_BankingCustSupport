"""
Feedback Handler Agent for the Banking Customer Support
Multi-Agent System.

Responsibilities:
- Handle positive customer feedback
- Handle negative customer feedback
- Generate ticket IDs for negative feedback
- Delegate persistence to the database layer
"""

import random

from utils.logger import log_event

# NOTE:
# Database functions will be implemented in database/db.py
# We import them here, but actual DB logic will come next.
from database.db import insert_ticket


# ------------------------------------------------------------------
# POSITIVE FEEDBACK HANDLER
# ------------------------------------------------------------------

def handle_positive_feedback(user_message: str, customer_name: str) -> str:
    """
    Handles positive customer feedback by returning
    a warm, personalized thank-you message.
    """

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
# NEGATIVE FEEDBACK HANDLER
# ------------------------------------------------------------------

def handle_negative_feedback(user_message: str, customer_name: str) -> str:
    """
    Handles negative customer feedback by:
    - Generating a unique 6-digit ticket number
    - Creating a new unresolved support ticket
    - Returning an empathetic response to the user
    """

    ticket_number = _generate_ticket_number()

    # Persist ticket (DB logic will be added in db.py)
    insert_ticket(
        ticket_number=ticket_number,
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


# ------------------------------------------------------------------
# HELPER FUNCTIONS
# ------------------------------------------------------------------

def _generate_ticket_number() -> int:
    """
    Generates a random 6-digit ticket number.

    Note:
    - Collision handling will be addressed at the DB layer
    """
    return random.randint(100000, 999999)
