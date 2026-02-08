"""
Query Handler Agent for the Banking Customer Support
Multi-Agent System.

Responsibilities:
- Handle ticket status queries
- Ask for ticket number when ticket-related intent is incomplete
- Handle general informational queries by opening new tickets
"""

import re
import random
import sqlite3
from typing import Optional

from utils.logger import log_event
from database.db import get_ticket_status, insert_ticket


# ------------------------------------------------------------------
# MAIN QUERY HANDLER
# ------------------------------------------------------------------

def handle_query(user_message: str) -> str:
    """
    Handles user queries.

    Logic:
    1. Greeting → polite response, no ticket
    2. Ticket number present → return ticket status
    3. Explicit ticket reference without number → ask for ticket number
    4. General informational query → open a new support ticket
    """

    message_lower = user_message.lower().strip()

    # --------------------------------------------------------------
    # CASE 0: Greeting / small-talk
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
    # CASE 1: Ticket number present → ticket status query
    # --------------------------------------------------------------
    ticket_number = _extract_ticket_number(user_message)

    if ticket_number is not None:
        status = get_ticket_status(ticket_number)

        if status:
            response = (
                f"Your ticket #{ticket_number} is currently marked as: {status}."
            )
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
    # CASE 2: Explicit ticket reference but no ticket number
    # --------------------------------------------------------------
    if "ticket" in message_lower:
        response = (
            "I can help with that. Please provide your ticket number so "
            "I can check the status for you."
        )

        log_event(
            agent="QueryHandlerAgent",
            input_text=user_message,
            output_text="Ticket reference without ticket number"
        )

        return response

    # --------------------------------------------------------------
    # CASE 3: General informational query → open new ticket (SAFE)
    # --------------------------------------------------------------
    ticket_number = _create_ticket_with_retry(user_message)

    if ticket_number is None:
        # Extremely rare: DB failure after retries
        response = (
            "We’re currently experiencing a technical issue while creating "
            "your support ticket. Please try again shortly."
        )

        log_event(
            agent="QueryHandlerAgent",
            input_text=user_message,
            output_text="Ticket creation failed after retries"
        )

        return response

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
# HELPER FUNCTIONS
# ------------------------------------------------------------------

def _extract_ticket_number(message: str) -> Optional[int]:
    """
    Extracts a 6-digit ticket number from the user message.
    """
    match = re.search(r"\b(\d{6})\b", message)
    return int(match.group(1)) if match else None


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
    for attempt in range(max_retries):
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

        except Exception as e:
            # Any other DB error — abort
            return None

    return None


def _is_greeting(message: str) -> bool:
    """
    Detects simple greetings or conversational fillers
    that should not trigger ticket creation.
    """
    greetings = {
        "hello",
        "hi",
        "hey",
        "good morning",
        "good afternoon",
        "good evening",
        "thanks",
        "thank you",
        "ok",
        "okay",
    }

    return message in greetings
