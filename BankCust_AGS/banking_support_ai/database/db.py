"""
Database layer for the Banking Customer Support
Multi-Agent System.

Uses SQLite for lightweight, file-based persistence.

Responsibilities:
- Create support_tickets table (if not exists)
- Insert new tickets
- Query ticket status
"""

import sqlite3
from pathlib import Path
from typing import Optional

import os
import sqlite3

# ------------------------------------------------------------------
# DATABASE PATH SETUP (CLOUD-SAFE)
# ------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "support_tickets.db")

# Ensure the directory exists (critical for Streamlit Cloud)
os.makedirs(BASE_DIR, exist_ok=True)


# ------------------------------------------------------------------
# DATABASE CONFIGURATION
# ------------------------------------------------------------------

DB_PATH = Path(__file__).resolve().parent / "support_tickets.db"


def _get_connection():
    """
    Creates and returns a SQLite database connection.
    """
    return sqlite3.connect(DB_PATH)


# ------------------------------------------------------------------
# TABLE INITIALIZATION
# ------------------------------------------------------------------

def initialize_database():
    """
    Creates the support_tickets table if it does not exist.
    """

    with _get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS support_tickets (
                ticket_number INTEGER PRIMARY KEY,
                issue_description TEXT NOT NULL,
                status TEXT NOT NULL
            )
        """)

        conn.commit()


# ------------------------------------------------------------------
# INSERT OPERATIONS
# ------------------------------------------------------------------

def insert_ticket(
    ticket_number: int,
    issue_description: str,
    status: str
) -> None:
    """
    Inserts a new support ticket into the database.

    Handles ticket number collisions gracefully.
    """

    initialize_database()

    with _get_connection() as conn:
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO support_tickets (
                    ticket_number,
                    issue_description,
                    status
                ) VALUES (?, ?, ?)
            """, (ticket_number, issue_description, status))

            conn.commit()

        except sqlite3.IntegrityError:
            # Ticket number collision (PRIMARY KEY constraint)
            # Re-raise so the caller can decide what to do
            raise


# ------------------------------------------------------------------
# QUERY OPERATIONS
# ------------------------------------------------------------------

def get_ticket_status(ticket_number: int) -> Optional[str]:
    """
    Retrieves the status of a ticket by ticket number.

    Returns:
    - status (str) if found
    - None if ticket does not exist
    """

    initialize_database()

    with _get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT status
            FROM support_tickets
            WHERE ticket_number = ?
        """, (ticket_number,))

        row = cursor.fetchone()

        if row:
            return row[0]

        return None
