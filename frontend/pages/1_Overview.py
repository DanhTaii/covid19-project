# frontend/pages/1_Overview.py
# Cách 1 – import tuyệt đối (khuyên dùng)
# frontend/pages/1_Overview.py
# frontend/pages/1_Overview.py

from style import set_custom_css
set_custom_css()

import streamlit as st
st.set_page_config(page_title="COVID-19 OVERVIEW", layout="wide")

import sys
import os

# Thêm backend vào sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend')))

from covid_app.services.overViewController import OverViewController

# Đường dẫn tới file Parquet
covid_data_path = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "..", "backend", "covid_app", "data", "cleaned_covid_data.parquet"
))

# Sidebar: chọn chế độ hiển thị
st.sidebar.header("Chế độ hiển thị")
mode = st.sidebar.radio("Chọn dữ liệu:", ["Total Cases", "Total Deaths"])

# Chuyển chế độ thành key
mode_key = "cases" if mode == "Total Cases" else "deaths"

# Khởi tạo controller
overview = OverViewController(covid_data_path)

# Vẽ bản đồ theo chế độ
fig = overview.world_map(mode=mode_key)
st.plotly_chart(fig, use_container_width=True)

