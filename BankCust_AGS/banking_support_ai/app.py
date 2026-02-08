"""
Streamlit UI for the Banking Customer Support
Multi-Agent System with session-based conversational memory.

Responsibilities:
- Accept user input
- Invoke the controller
- Display chat-style responses
- Maintain session-level memory
- Provide an optional admin/debug view
"""

import re
import sqlite3

import pandas as pd
import streamlit as st

from controller import handle_user_input


# ------------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------------

st.set_page_config(
    page_title="Banking Customer Support AI",
    page_icon="🏦",
    layout="centered"
)

st.title("🏦 Banking Customer Support AI Agent")
st.write(
    "This assistant handles customer feedback and queries using a "
    "multi-agent AI architecture with session-based memory."
)

# ------------------------------------------------------------------
# SESSION STATE INITIALIZATION
# ------------------------------------------------------------------

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "customer_name" not in st.session_state:
    st.session_state.customer_name = "Customer"

if "last_ticket_number" not in st.session_state:
    st.session_state.last_ticket_number = None


# ------------------------------------------------------------------
# CUSTOMER NAME INPUT
# ------------------------------------------------------------------

st.session_state.customer_name = st.text_input(
    "Customer Name",
    value=st.session_state.customer_name
)

# ------------------------------------------------------------------
# CHAT DISPLAY
# ------------------------------------------------------------------

st.markdown("### 💬 Conversation")

for role, message in st.session_state.chat_history:
    if role == "User":
        st.markdown(f"**🧑 User:** {message}")
    else:
        st.markdown(f"**🤖 Agent:** {message}")

# ------------------------------------------------------------------
# USER INPUT FORM
# ------------------------------------------------------------------

with st.form(key="chat_form", clear_on_submit=True):
    user_message = st.text_input(
        "Type your message",
        placeholder="e.g., My debit card has not arrived."
    )
    send_clicked = st.form_submit_button("Send")

# ------------------------------------------------------------------
# FORM SUBMISSION HANDLING
# ------------------------------------------------------------------

if send_clicked:

    if not user_message.strip():
        st.warning("Please enter a message before sending.")
    else:
        original_message = user_message

        # Resolve "last / my / previous ticket" using session memory
        if (
            st.session_state.last_ticket_number
            and re.search(r"\b(last|my|previous)\s+ticket\b", user_message.lower())
            and not re.search(r"\d{6}", user_message)
        ):
            user_message = (
                f"{user_message} "
                f"(ticket {st.session_state.last_ticket_number})"
            )

        # Store user message
        st.session_state.chat_history.append(
            ("User", original_message)
        )

        with st.spinner("Processing..."):
            response = handle_user_input(
                user_message=user_message,
                customer_name=st.session_state.customer_name
            )

        # Store agent response
        st.session_state.chat_history.append(
            ("Agent", response)
        )

        # Extract and remember ticket number
        match = re.search(r"#(\d{6})", response)
        if match:
            st.session_state.last_ticket_number = int(match.group(1))

        st.rerun()

# ------------------------------------------------------------------
# OPTIONAL CONTROLS
# ------------------------------------------------------------------

st.markdown("---")

if st.button("Clear conversation"):
    st.session_state.chat_history = []
    st.session_state.last_ticket_number = None
    st.rerun()

st.caption(
    "Session-based memory is maintained at the UI layer. "
    "Backend agents remain stateless."
)

# ------------------------------------------------------------------
# ADMIN / DEBUG VIEW (OPTIONAL)
# ------------------------------------------------------------------

with st.expander("🛠 Admin / Debug View"):
    st.write(
        "This section is intended for demonstration and debugging purposes. "
        "It displays all support tickets currently stored in the system."
    )

    try:
        from database.db import DB_PATH

        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        df = pd.read_sql_query(
            "SELECT ticket_number, issue_description, status FROM support_tickets",
            conn
        )
        conn.close()

        if df.empty:
            st.info("No tickets found in the system.")
        else:
            st.dataframe(df, width="stretch")

    except Exception as e:
        st.error(f"Unable to load tickets: {e}")
