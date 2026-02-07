"""
Centralized logging utility for the Banking Customer Support
Multi-Agent System.

Logs are written to both:
- Console (stdout) for local development
- File (logs/app.log) for persistence and debugging
"""

import logging
import os
from datetime import datetime


# ------------------------------------------------------------------
# LOG DIRECTORY SETUP
# ------------------------------------------------------------------

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE_PATH = os.path.join(LOG_DIR, "app.log")


# ------------------------------------------------------------------
# LOGGER CONFIGURATION
# ------------------------------------------------------------------

logger = logging.getLogger("BankCustAgentLogger")
logger.setLevel(logging.INFO)

# Prevent duplicate handlers on Streamlit reruns
if not logger.handlers:

    # File handler
    file_handler = logging.FileHandler(LOG_FILE_PATH)
    file_handler.setLevel(logging.INFO)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Log format
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


# ------------------------------------------------------------------
# PUBLIC LOGGING FUNCTION
# ------------------------------------------------------------------

def log_event(agent: str, input_text: str, output_text: str):
    """
    Logs an agent interaction in a structured format.
    """

    logger.info(
        f"[{agent}] INPUT: {input_text} | OUTPUT: {output_text}"
    )
