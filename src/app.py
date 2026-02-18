"""Streamlit entry point for LangChatbot.

Phase 1 — Minimal pipeline:
    Chat input → LangChain ChatOpenAI (via OpenRouter) → display response.
    No LangGraph, no tools, no file context, no sessions, no streaming.
    Just proof that the Streamlit ↔ LangChain ↔ OpenRouter pipeline works.

Run with:
    streamlit run src/app.py
"""

import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage

from src.config_loader import load_config
from src.llm_factory import create_llm

# --- Page configuration ---
st.set_page_config(page_title="LangChatbot", page_icon="💬")
st.title("LangChatbot")

# --- Load configuration ---
config = load_config()
default_model: str = str(config["default_model"])

# --- Initialise session state for chat history ---
# st.session_state persists across Streamlit reruns within the same browser
# session.  We store the list of LangChain message objects here so the chat
# UI can replay them on each rerun.
if "messages" not in st.session_state:
    st.session_state.messages: list[HumanMessage | AIMessage] = []

# --- Display existing chat history ---
for msg in st.session_state.messages:
    # LangChain message types map to Streamlit chat roles:
    #   HumanMessage  → "user"
    #   AIMessage     → "assistant"
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(msg.content)

# --- Handle new user input ---
if user_input := st.chat_input("Type a message…"):
    # 1. Append the user message and display it immediately.
    user_msg = HumanMessage(content=user_input)
    st.session_state.messages.append(user_msg)
    with st.chat_message("user"):
        st.markdown(user_input)

    # 2. Send the full conversation history to the LLM.
    #    Phase 1 uses direct llm.invoke() — no LangGraph yet.
    try:
        llm = create_llm(model=default_model)
        ai_response = llm.invoke(st.session_state.messages)
    except ValueError as exc:
        # Missing API key or config issue — show a friendly banner.
        st.error(str(exc))
        st.stop()
    except Exception as exc:
        st.error(f"LLM request failed: {exc}")
        st.stop()

    # 3. Append the assistant response and display it.
    st.session_state.messages.append(ai_response)
    with st.chat_message("assistant"):
        st.markdown(ai_response.content)
