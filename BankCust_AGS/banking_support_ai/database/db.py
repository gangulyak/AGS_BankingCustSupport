"""
Database layer for the Banking Customer Support
Multi-Agent System.

Uses SQLite for lightweight, file-based persistence.

Responsibilities:
- Create support_tickets table (if not exists)
- Insert new tickets
- Query ticket status
"""

import os
import sqlite3
from pathlib import Path
from typing import Optional


# ------------------------------------------------------------------
# DATABASE PATH SETUP (CLOUD-SAFE)
# ------------------------------------------------------------------

# Absolute path to this directory (banking_support_ai/database)
BASE_DIR = Path(__file__).resolve().parent

# Ensure directory exists (critical for Streamlit Cloud)
BASE_DIR.mkdir(parents=True, exist_ok=True)

# Absolute path to database file
DB_PATH = BASE_DIR / "support_tickets.db"


# ------------------------------------------------------------------
# DATABASE CONNECTION
# ------------------------------------------------------------------

def _get_connection():
    """
    Creates and returns a SQLite database connection.
    """
    return sqlite3.connect(DB_PATH, check_same_thread=False)


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

    Raises sqlite3.IntegrityError on ticket number collision.
    """

    initialize_database()

    with _get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO support_tickets (
                ticket_number,
                issue_description,
                status
            ) VALUES (?, ?, ?)
        """, (ticket_number, issue_description, status))

        conn.commit()


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

        return row[0] if row else None
