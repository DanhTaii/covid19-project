# frontend/pages/1_Overview.py
import streamlit as st
import requests
import plotly.express as px
import pandas as pd
from style import set_custom_css

# Áp dụng CSS (nếu bạn có file style.py)
set_custom_css()

# Cấu hình trang
st.set_page_config(
    page_title="COVID-19 World Overview",
    page_icon="🌍",
    layout="wide"
)

# ==================== THÔNG TIN API ====================
DJANGO_API = "http://localhost:8000/api/visualization/world-map/"

# ==================== TIÊU ĐỀ + SIDEBAR ====================
st.title("🌍 Tổng quan COVID-19 Toàn cầu")
st.markdown("---")

col1, col2 = st.columns([1, 4])
with col1:
    mode = st.radio(
        "Chọn dữ liệu:",
        options=["Total Cases", "Total Deaths"],
        index=0,
        help="Hiển thị tổng ca nhiễm hoặc tổng tử vong theo quốc gia"
    )
with col2:
    st.write("")  # để căn đều

mode_key = "cases" if mode == "Total Cases" else "deaths"

# ==================== GỌI API TỪ DJANGO ====================
@st.cache_data(ttl=3600, show_spinner="Đang tải dữ liệu từ server...")
def load_world_map_data(mode):
    try:
        response = requests.get(DJANGO_API, params={"mode": mode}, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        st.error("Không kết nối được với Backend Django!")
        st.info("Django có đang chạy không? → http://localhost:8000")
        st.stop()

data = load_world_map_data(mode_key)

# ==================== VẼ BẢN ĐỒ ====================
df = pd.DataFrame({
    "Country Name": data["locations"],
    "Value": data["values"]
})


fig = px.choropleth(
    data_frame=df,
    locations="Country Name",  # ✅ ĐÚNG: Tên cột trong DataFrame
    locationmode="country names",
    color="Value",  # ✅ ĐÚNG: Tên cột trong DataFrame
    color_continuous_scale="Reds" if mode_key == "cases" else "Blues",
    title=data["title"],
    labels={"color": "Tổng ca nhiễm" if mode_key == "cases" else "Tổng tử vong"},
    hover_name="Country Name",  # ✅ ĐÚNG: Tên cột trong DataFrame
    hover_data={
        "Value": ":,",  # ✅ ĐÚNG: Format áp dụng cho tên cột "Value"
        "Country Name": False  # ✅ ĐÚNG: Ẩn cột "Country Name"
    }
)

fig.update_geos(
    projection_type="natural earth",
    showframe=False,
    showcoastlines=True,
    coastlinecolor="Gray",
    showland=True,
    landcolor="lightgray"
)

fig.update_layout(
    height=700,
    margin={"r": 0, "t": 80, "l": 0, "b": 0},
    title_x=0.5,
    title_font_size=24
)

st.plotly_chart(fig, use_container_width=True)

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend')))
#
# # Import class từ backend
# from covid_app.services.visualizationController import CovidVisualizerOO
#
# st.title("COVID-19 Visualization")
#
# # Đường dẫn tới file Parquet
# covid_data_path = os.path.abspath(os.path.join(
#     os.path.dirname(__file__), "..", "..", "backend", "covid_app", "data", "cleaned_covid_data.parquet"
# ))
#
# # Khởi tạo visualizer
# visualizer = CovidVisualizerOO(covid_data_path)
#
# # Chọn quốc gia
# available_countries = visualizer.get_available_countries()
# country = st.selectbox("Select country", available_countries)
#
# # Vẽ biểu đồ số ca
# fig_cases = visualizer.plot_cases(country)
# st.pyplot(fig_cases)
#
# # Vẽ biểu đồ tử vong
# fig_deaths = visualizer.plot_deaths(country)
# st.pyplot(fig_deaths)
