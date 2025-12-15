import streamlit as st
import requests
import plotly.express as px
import pandas as pd
from style import set_custom_css

set_custom_css()

st.set_page_config(
    page_title="COVID-19 World Overview",
    page_icon="🌍",
    layout="wide"
)

DJANGO_API = "http://localhost:8000/api/visualization/world-map/"

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
    st.write("")

mode_key = "cases" if mode == "Total Cases" else "deaths"

@st.cache_data(ttl=3600, show_spinner="Đang tải dữ liệu từ server...")
def load_world_map_data(mode):
    try:
        response = requests.get(DJANGO_API, params={"mode": mode}, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        st.error("Không kết nối được với Backend Django!")
        st.stop()

data = load_world_map_data(mode_key)

# ==================== VẼ BẢN ĐỒ ====================
df = pd.DataFrame({
    "Country Name": data["locations"],
    "Value": data["values"]
})

fig = px.choropleth(
    data_frame=df,
    locations="Country Name",
    locationmode="country names",
    color="Value",
    color_continuous_scale="Reds" if mode_key == "cases" else "Blues",
    title=data["title"],
    labels={"color": "Tổng ca nhiễm" if mode_key == "cases" else "Tổng tử vong"},
    hover_name="Country Name",
    hover_data={"Value": ":,", "Country Name": False}
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

# ==================== VẼ BIỂU ĐỒ ĐƯỜNG TOÀN CẦU ====================
trends = data["global_trends"]

df_trends = pd.DataFrame({
    "Date": trends["dates"],
    "Total Cases": trends["cases"],
    "Total Deaths": trends["deaths"]
})

fig_cases = px.line(
    df_trends,
    x="Date",
    y="Total Cases",
    title="📈 Total number of cases globally",
    labels={"Total Cases": "Cases"}
)
fig_cases.update_layout(height=400, title_x=0.5)
st.plotly_chart(fig_cases, use_container_width=True)

fig_deaths = px.line(
    df_trends,
    x="Date",
    y="Total Deaths",
    title="📉 Total global deaths",
    labels={"Total Deaths": "Deaths"}
)
fig_deaths.update_layout(height=400, title_x=0.5)
st.plotly_chart(fig_deaths, use_container_width=True)
