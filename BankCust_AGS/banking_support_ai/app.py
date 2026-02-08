import re
import sqlite3
import gradio as gr
import pandas as pd

from controller import handle_user_input
from database.db import DB_PATH


# ------------------------------------------------------------
# SESSION MEMORY (Gradio-managed)
# ------------------------------------------------------------

def init_state():
    return {
        "last_ticket_number": None
    }


# ------------------------------------------------------------
# CHAT HANDLER
# ------------------------------------------------------------

def chat_handler(message, chat_history, customer_name, state):
    """
    Handles one user turn and returns updated chat.
    """

    # Resolve "last / my / previous ticket"
    if (
        state["last_ticket_number"]
        and re.search(r"\b(last|my|previous)\s+ticket\b", message.lower())
        and not re.search(r"\d{6}", message)
    ):
        message = f"{message} (ticket {state['last_ticket_number']})"

    # Get response from backend
    response = handle_user_input(
        user_message=message,
        customer_name=customer_name
    )

    # Store last ticket number if present
    match = re.search(r"#(\d{6})", response)
    if match:
        state["last_ticket_number"] = int(match.group(1))

    chat_history.append((message, response))
    return chat_history, state


# ------------------------------------------------------------
# ADMIN VIEW
# ------------------------------------------------------------

def load_tickets():
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(
            "SELECT ticket_number, issue_description, status FROM support_tickets",
            conn
        )
        conn.close()

        if df.empty:
            return "No tickets found."
        return df

    except Exception as e:
        return f"Error loading tickets: {e}"


# ------------------------------------------------------------
# GRADIO UI
# ------------------------------------------------------------

with gr.Blocks(title="Banking Customer Support AI") as demo:

    gr.Markdown("## 🏦 Banking Customer Support AI Agent")
    gr.Markdown(
        "This assistant handles customer feedback and queries using a "
        "multi-agent AI architecture with session-based memory."
    )

    state = gr.State(init_state())

    customer_name = gr.Textbox(
        label="Customer Name",
        value="Customer"
    )

    chatbot = gr.Chatbot(label="Conversation")

    user_input = gr.Textbox(
        label="Type your message",
        placeholder="e.g., My debit card has not arrived."
    )

    send_btn = gr.Button("Send")

    send_btn.click(
        chat_handler,
        inputs=[user_input, chatbot, customer_name, state],
        outputs=[chatbot, state]
    )

    user_input.submit(
        chat_handler,
        inputs=[user_input, chatbot, customer_name, state],
        outputs=[chatbot, state]
    )

    gr.Markdown("---")

    with gr.Accordion("🛠 Admin / Debug View", open=False):
        admin_output = gr.Dataframe()
        refresh_btn = gr.Button("Refresh Tickets")

        refresh_btn.click(
            load_tickets,
            outputs=admin_output
        )


# ------------------------------------------------------------
# RUN
# ------------------------------------------------------------

if __name__ == "__main__":
    demo.launch()
