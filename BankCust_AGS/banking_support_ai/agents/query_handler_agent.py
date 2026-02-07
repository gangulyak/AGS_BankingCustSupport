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
from typing import Optional

from utils.logger import log_event
from database.db import get_ticket_status, insert_ticket


# ------------------------------------------------------------------
# MAIN QUERY HANDLER
# ------------------------------------------------------------------

def handle_query(user_message: str) -> str:
    """
    Handles user queries.
    """

    # ✅ NEW: Greeting / small-talk guard
    if _is_greeting(user_message):
        response = (
            "Hello! How can I assist you today?"
        )

        log_event(
            agent="QueryHandlerAgent",
            input_text=user_message,
            output_text="Greeting detected – no ticket created"
        )

        return response

    """
    Handles user queries.

    Logic:
    1. If ticket number is present → return ticket status
    2. If ticket-related intent but no ticket number → ask for ticket number
    3. If general query → open a new support ticket
    """

    ticket_number = _extract_ticket_number(user_message)

    # --------------------------------------------------------------
    # CASE 1: Ticket number present → ticket status query
    # --------------------------------------------------------------
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
    # CASE 2: Ticket-related intent but no ticket number
    # --------------------------------------------------------------
    if _is_ticket_related_query(user_message):
        response = (
            "I can help with that. Please provide your ticket number so "
            "I can check the status for you."
        )

        log_event(
            agent="QueryHandlerAgent",
            input_text=user_message,
            output_text="Ticket-related query without ticket number"
        )

        return response

    # --------------------------------------------------------------
    # CASE 3: General informational query → open new ticket
    # --------------------------------------------------------------
    new_ticket_number = _generate_ticket_number()

    insert_ticket(
        ticket_number=new_ticket_number,
        issue_description=user_message,
        status="Open"
    )

    response = (
        "Thank you for reaching out. "
        f"I’ve created a support ticket #{new_ticket_number} so our team can "
        "get back to you with the information you requested."
    )

    log_event(
        agent="QueryHandlerAgent",
        input_text=user_message,
        output_text=f"General query logged with ticket #{new_ticket_number}"
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


def _is_ticket_related_query(message: str) -> bool:
    """
    Determines whether a query is ticket-related
    without explicitly providing a ticket number.
    """
    message = message.lower()

    ticket_keywords = [
        "ticket",
        "status",
        "issue",
        "complaint",
        "request",
        "case"
    ]

    return any(keyword in message for keyword in ticket_keywords)


def _generate_ticket_number() -> int:
    """
    Generates a random 6-digit ticket number.
    """
    return random.randint(100000, 999999)

def _is_greeting(message: str) -> bool:
    """
    Detects simple greetings or conversational fillers
    that should not trigger ticket creation.
    """
    message = message.lower().strip()

    greetings = [
        "hello",
        "hi",
        "hey",
        "good morning",
        "good afternoon",
        "good evening",
        "thanks",
        "thank you",
        "ok",
        "okay"
    ]

    return message in greetings
