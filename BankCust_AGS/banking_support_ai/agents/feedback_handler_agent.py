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
import sqlite3
from typing import Optional

from utils.logger import log_event
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
# NEGATIVE FEEDBACK HANDLER (ROBUST)
# ------------------------------------------------------------------

def handle_negative_feedback(user_message: str, customer_name: str) -> str:
    """
    Handles negative customer feedback by:
    - Safely generating a unique 6-digit ticket number
    - Creating a new unresolved support ticket
    - Returning an empathetic response to the user
    """

    ticket_number = _create_ticket_with_retry(user_message)

    if ticket_number is None:
        # Extremely rare DB failure case
        response = (
            "We’re sorry for the inconvenience. "
            "We’re currently experiencing a technical issue while creating "
            "your support ticket. Please try again shortly."
        )

        log_event(
            agent="FeedbackHandlerAgent",
            input_text=user_message,
            output_text="Negative feedback received but ticket creation failed"
        )

        return response

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

def _create_ticket_with_retry(
    issue_description: str,
    max_retries: int = 5
) -> Optional[int]:
    """
    Attempts to create a support ticket, retrying on
    ticket number collisions.

    Returns:
    - ticket_number if successful
    - None if all retries fail
    """

    for _ in range(max_retries):
        ticket_number = random.randint(100000, 999999)

        try:
            insert_ticket(
                ticket_number=ticket_number,
                issue_description=issue_description,
                status="Open"
            )
            return ticket_number

        except sqlite3.IntegrityError:
            # Ticket number collision — retry
            continue

        except Exception:
            # Any other DB error — abort
            return None

    return None
