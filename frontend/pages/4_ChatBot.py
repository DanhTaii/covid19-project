from http.client import responses
from pickle import FALSE

import requests
import streamlit as st
from click import prompt
from style import set_custom_css
import time

st.title("Promt vs ChatGPT")

API_BASE = "http://localhost:8000/api/chatbot"


@st.cache_data(ttl= 3600, show_spinner= FALSE )
def fetch_data(url, params = None):
    try:
        responses = requests.get(url, params=params, timeout=15)
        responses.raise_for_status()
        return responses.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Lỗi kết nỗi API")
        return None

@st.cache_data(ttl=3600)
def get_answer():
    url = f"{API_BASE}"


if "messages" not in st.session_state:
    st.session_state.messages = []

if prompt := st.chat_input("Hãy nhập vào yêu cầu !"):
    # Dictionary
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )
    # Dùng markdown để in ra prompt
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        full_res = ""
        holder = st.empty()

        for word in prompt.split():
            full_res += word + " "
            time.sleep(0.05)
            holder.markdown(full_res + "█ ")
        holder.markdown(full_res + " ")

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": full_res
        }
    )
