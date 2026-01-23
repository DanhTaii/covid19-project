from http.client import responses
from pickle import FALSE

import requests
import streamlit as st
from click import prompt
from style import set_custom_css
import time

st.title("🤖 Covid-19 Assistant")

API_BASE = "http://localhost:8000/api/chatbot/rag/"

# # Khởi tạo lịch sử tin nhắn nếu chưa có
# if "messages" not in st.session_state:
#     st.session_state.messages = []
#
# # Hiển thị lại các tin nhắn cũ trong lịch sử
# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])

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

# Hiển thị lại lịch sử chat khi load trang
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- PHẦN XỬ LÝ CHÍNH ---
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

        with st.spinner("Đang truy vấn kho dữ liệu..."):
            try:
                # Gửi request POST sang Django
                response = requests.post(
                    API_BASE,
                    json={"question": prompt},  # Key 'question' phải khớp với backend/views.py
                    timeout=30
                )

                if response.status_code == 200:
                    # LẤY CÂU TRẢ LỜI THẬT TỪ AI
                    ai_answer = response.json().get("answer", "Xin lỗi, tôi không tìm thấy câu trả lời.")
                else:
                    ai_answer = f"Lỗi phía Server: {response.status_code}. Vui lòng kiểm tra Backend."

            except Exception as e:
                ai_answer = f"Không thể kết nối tới Backend. Lỗi: {str(e)}"

        for word in ai_answer.split():
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
