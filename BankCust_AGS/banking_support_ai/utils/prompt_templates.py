"""
Prompt templates used across agents in the Banking Customer Support
Multi-Agent System.

This file defines strict prompt contracts to ensure deterministic
LLM behavior and safe downstream routing.
"""


CLASSIFIER_PROMPT = """
You are a banking customer support classifier.

Your task is to classify the user's message into exactly ONE of the
following categories:

- positive_feedback
- negative_feedback
- query

Classification rules:
- Positive feedback expresses gratitude, appreciation, or satisfaction.
- Negative feedback expresses complaints, dissatisfaction, or unresolved issues.
- A query asks for information, clarification, or ticket status updates.

IMPORTANT:
- Return ONLY the category label.
- Do NOT include explanations.
- Do NOT include punctuation or formatting.
- Do NOT include extra text.

User message:
\"\"\"{message}\"\"\"
"""
