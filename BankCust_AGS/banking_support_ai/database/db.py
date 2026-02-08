"""
Database layer for the Banking Customer Support
Multi-Agent System.

Uses SQLite for lightweight, file-based persistence.

Responsibilities:
- Create support_tickets table (if not exists)
- Insert new tickets (collision-safe)
- Query ticket status
"""

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
# INSERT OPERATIONS (ROBUST)
# ------------------------------------------------------------------

def insert_ticket(
    ticket_number: int,
    issue_description: str,
    status: str
) -> None:
    """
    Inserts a new support ticket into the database.

    Raises:
    - sqlite3.IntegrityError if ticket_number already exists
    - sqlite3.DatabaseError for other DB issues
    """

    initialize_database()

    try:
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

    except sqlite3.IntegrityError as e:
        # Ticket number collision (PRIMARY KEY)
        print(f"❌ DB INSERT FAILED (collision): ticket #{ticket_number}")
        raise

    except sqlite3.DatabaseError as e:
        # Any other SQLite-related error
        print(f"❌ DB INSERT FAILED (database error): {e}")
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

        return row[0] if row else None
