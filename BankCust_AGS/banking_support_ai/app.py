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
# SESSION STATE
# ------------------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "customer_name" not in st.session_state:
    st.session_state.customer_name = "Customer"

if "last_ticket_number" not in st.session_state:
    st.session_state.last_ticket_number = None


# ------------------------------------------------------------------
# CUSTOMER NAME
# ------------------------------------------------------------------

st.session_state.customer_name = st.text_input(
    "Customer Name",
    value=st.session_state.customer_name
)


# ------------------------------------------------------------------
# CHAT DISPLAY
# ------------------------------------------------------------------

for role, content in st.session_state.messages:
    with st.chat_message(role):
        st.markdown(content)


# ------------------------------------------------------------------
# ADMIN / DEBUG VIEW
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
            st.dataframe(df)

    except Exception as e:
        st.error(f"Unable to load tickets: {e}")


# ------------------------------------------------------------------
# CHAT INPUT (MUST BE LAST)
# ------------------------------------------------------------------

user_message = st.chat_input("Type your message")

if user_message:
    original_message = user_message

    if (
        st.session_state.last_ticket_number
        and re.search(r"\b(last|my|previous)\s+ticket\b", user_message.lower())
        and not re.search(r"\d+", user_message)
    ):
        user_message = (
            f"{user_message} "
            f"(ticket {st.session_state.last_ticket_number})"
        )

    st.session_state.messages.append(("user", original_message))

    response = handle_user_input(
        user_message=user_message,
        customer_name=st.session_state.customer_name
    )

    st.session_state.messages.append(("assistant", response))

    match = re.search(r"#(\d+)", response)
    if match:
        st.session_state.last_ticket_number = int(match.group(1))

    st.rerun()


# ------------------------------------------------------------------
# CLEAR
# ------------------------------------------------------------------

if st.button("Clear conversation"):
    st.session_state.messages = []
    st.session_state.last_ticket_number = None
    st.rerun()


st.caption(
    "Session-based memory is maintained at the UI layer. "
    "Backend agents remain stateless."
)
