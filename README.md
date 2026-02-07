{\rtf1\ansi\ansicpg1252\cocoartf2867
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx566\tx1133\tx1700\tx2267\tx2834\tx3401\tx3968\tx4535\tx5102\tx5669\tx6236\tx6803\pardirnatural\partightenfactor0

\f0\fs24 \cf0 # Banking Customer Support AI Agent\
### A Multi-Agent Generative AI System\
\
## Overview\
\
This project implements a **multi-agent AI assistant for banking customer support** using a combination of **Large Language Models (LLMs)** and **deterministic agent-based workflows**. The system is designed to handle customer feedback, service-related queries, and support ticket tracking in a scalable, explainable, and production-oriented manner.\
\
The application is deployed using **Streamlit** and demonstrates how GenAI can be integrated responsibly into enterprise-style workflows by restricting LLM usage to intent classification while keeping core business logic deterministic.\
\
---\
\
## Key Features\
\
- LLM-based classification of unstructured customer messages  \
- Multi-agent architecture with clear separation of responsibilities  \
- Automatic ticket creation and tracking using SQLite  \
- Graceful handling of ambiguity and conversational edge cases  \
- Session-based conversational memory at the UI layer  \
- Optional admin/debug view for ticket inspection  \
- Cloud-ready deployment on Streamlit Cloud  \
\
---\
\
## System Architecture (High-Level)\
\
1. **Streamlit UI (`app.py`)**  \
   Provides a chat-style interface, manages session memory, and captures user input.\
\
2. **Controller (`controller.py`)**  \
   Acts as the orchestration layer. It:\
   - Initializes the LLM\
   - Invokes the classifier agent\
   - Applies fallback handling\
   - Routes requests to the appropriate downstream agent\
\
3. **Agents (`agents/`)**\
   - **Classifier Agent**: Uses an LLM to classify input into predefined intent categories  \
   - **Feedback Handler Agent**: Handles positive feedback and creates tickets for negative feedback  \
   - **Query Handler Agent**: Manages ticket status queries, general informational queries, and conversational edge cases (e.g., greetings)\
\
4. **Database Layer (`database/db.py`)**  \
   Uses SQLite to persist support tickets and retrieve ticket status.\
\
5. **Utilities (`utils/`)**\
   - **Prompt templates** for consistent LLM interaction  \
   - **Logging utility** for structured logging to file and console  \
\
---\
\
## Intent Handling Logic\
\
Customer messages are classified into one of the following categories:\
\
- **Positive Feedback** \uc0\u8594  Generates a personalized acknowledgment  \
- **Negative Feedback** \uc0\u8594  Creates a new support ticket  \
- **Query**:\
  - Ticket number present \uc0\u8594  Returns ticket status  \
  - Ticket-related but incomplete \uc0\u8594  Asks for ticket number  \
  - General informational query \uc0\u8594  Creates a support ticket  \
  - Greeting / small talk \uc0\u8594  Responds politely without creating a ticket  \
\
This design ensures realistic banking support behavior while avoiding unnecessary ticket creation.\
\
---\
\
## Conversational Memory\
\
- Backend services are **stateless**\
- **Session-level memory** is implemented at the UI layer using Streamlit session state\
- A lightweight **last-ticket memory** improves usability by resolving references such as \'93my last ticket\'94 within a session\
\
---\
\
## Logging and Observability\
\
All agent interactions and routing decisions are logged using Python\'92s logging framework:\
\
- Logs are written to:\
  - Console (stdout) for local development\
  - A file (`logs/app.log`) for persistence and debugging\
- This supports transparency, debugging, and evaluation without exposing logs to end users\
\
---\
\
## Deployment Notes\
\
- The application is deployed on **Streamlit Cloud**\
- API keys are managed via **environment variables / Streamlit Secrets**\
- SQLite provides lightweight persistence during runtime (database resets on redeploy, which is acceptable for demonstration purposes)\
\
---\
\
## Directory Structure\
\
banking_support_ai/\
\uc0\u9474 \
\uc0\u9500 \u9472 \u9472  app.py                 # Streamlit UI and session memory\
\uc0\u9500 \u9472 \u9472  controller.py          # Central routing and orchestration\
\uc0\u9474 \
\uc0\u9500 \u9472 \u9472  agents/\
\uc0\u9474    \u9500 \u9472 \u9472  classifier_agent.py\
\uc0\u9474    \u9500 \u9472 \u9472  feedback_handler_agent.py\
\uc0\u9474    \u9492 \u9472 \u9472  query_handler_agent.py\
\uc0\u9474 \
\uc0\u9500 \u9472 \u9472  database/\
\uc0\u9474    \u9500 \u9472 \u9472  db.py\
\uc0\u9474    \u9492 \u9472 \u9472  support_tickets.db\
\uc0\u9474 \
\uc0\u9500 \u9472 \u9472  utils/\
\uc0\u9474    \u9500 \u9472 \u9472  logger.py\
\uc0\u9474    \u9492 \u9472 \u9472  prompt_templates.py\
\uc0\u9474 \
\uc0\u9492 \u9472 \u9472  requirements.txt\
\
\
\
---\
\
## Summary\
\
This project demonstrates a clean and realistic approach to building GenAI-powered support systems by combining language intelligence with robust software engineering principles. The resulting system is modular, explainable, and aligned with real-world banking support workflows.\
}