# frontend/pages/1_Overview.py
# Cách 1 – import tuyệt đối (khuyên dùng)
from style import set_custom_css   # ← DÙNG CÁI NÀY
set_custom_css()

import streamlit as st
st.set_page_config(page_title="COVID-19", layout="wide")