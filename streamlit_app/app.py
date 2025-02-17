import streamlit as st
from sidebar import display_sidebar
from chat_interface import display_chat_interface

st.title("RAG FastAPI Chatbot")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = None

display_sidebar()

display_chat_interface()