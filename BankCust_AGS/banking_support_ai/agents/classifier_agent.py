"""
LLM-based classifier agent for the Banking Customer Support
Multi-Agent System.

Responsibilities:
- Uses a Large Language Model (LLM) to classify user messages
- Enforces strict output constraints
- Signals when a safe fallback is applied

This agent performs classification ONLY.
All routing decisions are handled by the controller.
"""

from utils.prompt_templates import CLASSIFIER_PROMPT


def classify_message_llm(message: str, llm) -> tuple[str, bool]:
    """
    Classifies a user message using an LLM.

    Parameters:
    ----------
    message : str
        The raw user input message.
    llm : object
        An initialized LLM instance with an .invoke(prompt) method.

    Returns:
    -------
    label : str
        One of the allowed classification labels:
        - positive_feedback
        - negative_feedback
        - query

    fallback_used : bool
        True if the system fell back to 'query' due to:
        - LLM failure
        - Invalid or unexpected LLM output
    """

    prompt = CLASSIFIER_PROMPT.format(message=message)

    try:
        response = llm.invoke(prompt)
        label = response.strip().lower()

    except Exception:
        # LLM invocation failed → safe fallback
        return "query", True

    allowed_labels = {
        "positive_feedback",
        "negative_feedback",
        "query"
    }

    if label not in allowed_labels:
        # LLM returned an unexpected or hallucinated label
        return "query", True

    return label, False
