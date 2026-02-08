"""
LLM-based classifier agent for the Banking Customer Support
Multi-Agent System.

Responsibilities:
- Uses a Large Language Model (LLM) to classify user messages
- Enforces strict output constraints
- Normalizes and validates LLM output
- Signals when a safe fallback is applied

This agent performs classification ONLY.
All routing decisions are handled by the controller.
"""

import re
from utils.prompt_templates import CLASSIFIER_PROMPT


# ------------------------------------------------------------------
# CLASSIFIER
# ------------------------------------------------------------------

def classify_message_llm(message: str, llm) -> tuple[str, bool]:
    """
    Classifies a user message using an LLM.

    Returns:
    -------
    label : str
        One of:
        - positive_feedback
        - negative_feedback
        - query

    fallback_used : bool
        True if the system fell back to 'query' due to
        invalid, ambiguous, or failed LLM output.
    """

    prompt = CLASSIFIER_PROMPT.format(message=message)

    try:
        raw_response = llm.invoke(prompt)
    except Exception:
        # LLM invocation failed → safe fallback
        return "query", True

    # --------------------------------------------------------------
    # NORMALIZE LLM OUTPUT
    # --------------------------------------------------------------
    label = _normalize_label(raw_response)

    # --------------------------------------------------------------
    # VALIDATE OUTPUT
    # --------------------------------------------------------------
    if label not in _ALLOWED_LABELS:
        return "query", True

    return label, False


# ------------------------------------------------------------------
# NORMALIZATION & VALIDATION
# ------------------------------------------------------------------

_ALLOWED_LABELS = {
    "positive_feedback",
    "negative_feedback",
    "query",
}

_LABEL_SYNONYMS = {
    "positive": "positive_feedback",
    "praise": "positive_feedback",
    "compliment": "positive_feedback",

    "negative": "negative_feedback",
    "complaint": "negative_feedback",
    "issue": "negative_feedback",
    "problem": "negative_feedback",

    "question": "query",
    "inquiry": "query",
    "request": "query",
}


def _normalize_label(raw_response: str) -> str:
    """
    Cleans and normalizes raw LLM output into a canonical label.
    """

    if not raw_response:
        return ""

    # Lowercase and trim
    text = raw_response.strip().lower()

    # Remove punctuation and markdown noise
    text = re.sub(r"[^\w\s]", "", text)
    text = text.replace("\n", " ").strip()

    # Exact match
    if text in _ALLOWED_LABELS:
        return text

    # Common variants (e.g., "negative feedback")
    text = text.replace(" ", "_")
    if text in _ALLOWED_LABELS:
        return text

    # Synonym mapping
    for keyword, canonical_label in _LABEL_SYNONYMS.items():
        if keyword in text:
            return canonical_label

    # Nothing matched → invalid
    return ""
