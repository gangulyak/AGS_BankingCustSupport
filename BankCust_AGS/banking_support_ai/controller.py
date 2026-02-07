"""
Controller module for the Banking Customer Support Multi-Agent System.

Responsibilities:
- Instantiate the LLM used across agents
- Receive raw user input
- Invoke the classifier agent
- Handle fallback scenarios explicitly
- Route the request to the appropriate downstream agent
"""

import os
import requests

from agents.classifier_agent import classify_message_llm
from agents.feedback_handler_agent import (
    handle_positive_feedback,
    handle_negative_feedback
)
from agents.query_handler_agent import handle_query
from utils.logger import log_event


# ------------------------------------------------------------------
# OPENROUTER LLM WRAPPER
# ------------------------------------------------------------------

class OpenRouterLLM:
    """
    Minimal OpenRouter LLM wrapper.

    Contract:
    - invoke(prompt: str) -> str
    """

    def __init__(
        self,
        model: str = "meta-llama/llama-3.1-8b-instruct",
        temperature: float = 0.0
    ):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not set")

        self.model = model
        self.temperature = temperature
        self.url = "https://openrouter.ai/api/v1/chat/completions"

    def invoke(self, prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            # Optional but recommended by OpenRouter
            "HTTP-Referer": "http://localhost",
            "X-Title": "BankCust_AGS"
        }

        payload = {
            "model": self.model,
            "temperature": self.temperature,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        response = requests.post(
            self.url,
            headers=headers,
            json=payload,
            timeout=30
        )

        response.raise_for_status()

        return response.json()["choices"][0]["message"]["content"]


# ------------------------------------------------------------------
# LLM INITIALIZATION (Controller-owned)
# ------------------------------------------------------------------

def initialize_llm():
    """
    Initializes and returns an OpenRouter-hosted LLaMA model.

    Agents remain model-agnostic.
    """

    return OpenRouterLLM(
        model="meta-llama/llama-3.1-8b-instruct",
        temperature=0.0
    )


# ------------------------------------------------------------------
# MAIN CONTROLLER LOGIC
# ------------------------------------------------------------------

def handle_user_input(user_message: str, customer_name: str = "Customer") -> str:
    """
    Main entry point for handling user input.

    Steps:
    1. Initialize LLM
    2. Classify message using LLM-based classifier agent
    3. Log and handle fallback if needed
    4. Route request using explicit if-else logic
    5. Return final response to user
    """

    llm = initialize_llm()

    # --- STEP 1: CLASSIFICATION ---
    label, fallback_used = classify_message_llm(user_message, llm)

    log_event(
        agent="ClassifierAgent",
        input_text=user_message,
        output_text=f"label={label}, fallback_used={fallback_used}"
    )

    # --- STEP 2: FALLBACK HANDLING ---
    if fallback_used:
        log_event(
            agent="Controller",
            input_text=user_message,
            output_text="Fallback applied: treating input as 'query'"
        )

    # --- STEP 3: EXPLICIT ROUTING LOGIC ---
    if label == "positive_feedback":
        response = handle_positive_feedback(
            user_message=user_message,
            customer_name=customer_name
        )

    elif label == "negative_feedback":
        response = handle_negative_feedback(
            user_message=user_message,
            customer_name=customer_name
        )

    elif label == "query":
        response = handle_query(user_message)

    else:
        # Should never occur due to classifier safeguards
        response = (
            "We’re sorry, but we couldn’t process your request at the moment."
        )

    # --- STEP 4: FINAL LOGGING ---
    log_event(
        agent="Controller",
        input_text=user_message,
        output_text=response
    )

    return response
