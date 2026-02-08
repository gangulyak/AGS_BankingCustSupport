"""
Query Handler Agent for the Banking Customer Support
Multi-Agent System.
"""

import re
from typing import Optional

from utils.logger import log_event
from database.db import get_ticket_status, insert_ticket


def handle_query(user_message: str) -> str:
    """
    Handles user queries.

    Logic:
    1. Greeting → polite response
    2. Ticket number present → return status
    3. Explicit ticket reference without number → ask for number
    4. General informational query → create ticket
    """

    message_lower = user_message.lower().strip()

    # --------------------------------------------------------------
    # CASE 0: Greeting
    # --------------------------------------------------------------
    if _is_greeting(message_lower):
        response = "Hello! How can I assist you today?"

        log_event(
            agent="QueryHandlerAgent",
            input_text=user_message,
            output_text="Greeting detected – no ticket created"
        )
        return response

    # --------------------------------------------------------------
    # CASE 1: Ticket number present
    # --------------------------------------------------------------
    ticket_number = _extract_ticket_number(message_lower)

    if ticket_number is not None:
        status = get_ticket_status(ticket_number)

        if status:
            response = f"Your ticket #{ticket_number} is currently marked as: {status}."
        else:
            response = (
                f"We could not find a ticket with number #{ticket_number}. "
                "Please double-check the number and try again."
            )

        log_event(
            agent="QueryHandlerAgent",
            input_text=user_message,
            output_text=response
        )
        return response

    # --------------------------------------------------------------
    # CASE 2: Ticket reference without number
    # --------------------------------------------------------------
    if "ticket" in message_lower:
        response = (
            "I can help with that. Please provide your ticket number so "
            "I can check the status for you."
        )

        log_event(
            agent="QueryHandlerAgent",
            input_text=user_message,
            output_text="Ticket reference without number"
        )
        return response

    # --------------------------------------------------------------
    # CASE 3: General informational query → CREATE TICKET
    # --------------------------------------------------------------
    ticket_number = insert_ticket(
        issue_description=user_message,
        status="Open"
    )

    response = (
        "Thank you for reaching out. "
        f"I’ve created a support ticket #{ticket_number} so our team can "
        "get back to you with the information you requested."
    )

    log_event(
        agent="QueryHandlerAgent",
        input_text=user_message,
        output_text=f"General query logged with ticket #{ticket_number}"
    )

    return response


# ------------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------------

def _extract_ticket_number(message: str) -> Optional[int]:
    match = re.search(r"\b(\d+)\b", message)
    return int(match.group(1)) if match else None


def _is_greeting(message: str) -> bool:
    return message in {
        "hello", "hi", "hey",
        "good morning", "good afternoon", "good evening",
        "thanks", "thank you", "ok", "okay"
    }
