from __future__ import annotations

from typing import Any, Dict

import streamlit as st

from src.cred_support_agent.api.main import ask
from src.cred_support_agent.schemas.responses import AskRequest


st.set_page_config(
    page_title="Cred Domain Support Agent",
    page_icon="💬",
    layout="centered",
)

st.title("Cred Domain Support Agent")
st.caption("Local deterministic demo using illustrative project policies and synthetic application data.")
st.warning(
    "Demo only: do not enter real customer information, account numbers, or other sensitive data. "
    "The policy content is illustrative and is not official Cred policy."
)

with st.sidebar:
    st.header("Loan application lookup")
    record_id = st.text_input(
        "Synthetic record ID (optional)",
        placeholder="For example: CL-0001",
        help="Use a generated synthetic record ID only.",
    )
    st.caption("Ask a question below. If a record ID is provided, the demo includes its lookup result.")

st.session_state.setdefault("chat_history", [])

for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant" and message.get("details"):
            details = message["details"]
            st.caption(
                f"Status: {details['status']} · "
                f"Supported: {'yes' if details['supported'] else 'no'} · "
                f"Trace: {details['trace_id']}"
            )
            if details.get("record"):
                st.json(details["record"])

query = st.chat_input("Ask about an illustrative policy or synthetic loan application")

if query:
    st.session_state.chat_history.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    request = AskRequest(query=query, record_id=record_id.strip() or None)
    result: Dict[str, Any] = ask(request)
    response = {
        "status": result["status"],
        "supported": result["supported"],
        "trace_id": result["trace_id"],
        "record": result.get("record"),
    }

    with st.chat_message("assistant"):
        st.markdown(result["answer"])
        st.caption(
            f"Status: {response['status']} · "
            f"Supported: {'yes' if response['supported'] else 'no'} · "
            f"Trace: {response['trace_id']}"
        )
        if response["record"]:
            st.json(response["record"])

    st.session_state.chat_history.append(
        {
            "role": "assistant",
            "content": result["answer"],
            "details": response,
        }
    )

if not st.session_state.chat_history:
    st.markdown("### Try a sample question")
    st.markdown(
        "- What are the general eligibility requirements for a home loan?\n"
        "- How is the EMI on a loan typically computed?\n"
        "- What is the weather in Mumbai today?"
    )
