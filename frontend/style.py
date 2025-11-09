# style.py (tạo file riêng hoặc dán vào app.py)
import streamlit as st

def set_custom_css():
    st.markdown("""
    <style>
    /* Đổi màu nền sidebar */
    [data-testid="stSidebar"] {
        background-color: #002333;  /* Màu xanh đậm */
    }

    /* ===== TẤT CẢ CHỮ TRONG SIDEBAR THÀNH TRẮNG ===== */
    [data-testid="stSidebar"] * {
        color: white !important;
    }

    /* Đổi màu nền chính (main content) */
    .main .block-container {
        background-color: #f8fafc;
        padding-top: 2rem;
    }

    # /* Đổi màu tiêu đề */
    # h1, h2, h3 {
    #     color: #FFFFFF;
    # }

    # /* Ẩn header Streamlit mặc định */
    # #MainMenu {visibility: hidden;}
    # footer {visibility: hidden;}
    # </style>
    # """, unsafe_allow_html=True)