import streamlit as st
import requests
import plotly.express as px
import pandas as pd
import time
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

def load_world_map_data(mode: str):
    try:
        params = {"mode": mode, "cache_buster": int(time.time() * 1000)}  # Thêm *1000 để khác nhanh hơn
        response = requests.get(DJANGO_API, params=params, timeout=15)
        response.raise_for_status()
        print("DEBUG RESPONSE:", response.json())  # Thêm dòng này tạm để xem console Streamlit
        return response.json()
    except Exception as e:
        st.error(f"Lỗi: {e}")
        return None

data = load_world_map_data(mode_key)

# ==================== VẼ BẢN ĐỒ ====================
df_map = pd.DataFrame({
    "Country Name": data["locations"],
    "Value": data["values"]
})

fig = px.choropleth(
    data_frame=df_map,
    locations="Country Name",
    locationmode="country names",
    color="Value",
    color_continuous_scale="Reds" if mode_key == "cases" else "Blues",
    title=data["title"],
    labels={"Value": "Tổng ca nhiễm" if mode_key == "cases" else "Tổng tử vong"},
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

fig.update_layout(height=700, margin={"r": 0, "t": 80, "l": 0, "b": 0}, title_x=0.5, title_font_size=24)
st.plotly_chart(fig, use_container_width=True)

# ==================== BIỂU ĐỒ ĐƯỜNG ====================
st.markdown("---")
st.subheader("📊 Xu hướng toàn cầu theo thời gian")

trend_mode = st.radio(
    "Chọn loại dữ liệu hiển thị:",
    options=["Total Cases", "Total Deaths"],
    index=0,
    horizontal=True
)

df_trends = pd.DataFrame({
    "Date": data["global_trends"]["dates"],
    "Total Cases": data["global_trends"]["cases"],
    "Total Deaths": data["global_trends"]["deaths"]
})

y_col = "Total Cases" if trend_mode == "Total Cases" else "Total Deaths"

fig_trend = px.line(df_trends, x="Date", y=y_col, title=f"Xu hướng {trend_mode.lower()} toàn cầu")
fig_trend.update_layout(height=450, title_x=0.5, margin={"r": 0, "t": 60, "l": 0, "b": 0})
st.plotly_chart(fig_trend, use_container_width=True)

# ==================== TOP 10 ====================
st.markdown("---")
st.subheader("🏆 Top 10 quốc gia")

top_mode = st.radio(
    "Chọn dữ liệu hiển thị:",
    options=["Total Cases", "Total Deaths"],
    index=0,
    horizontal=True
)

if "top10" in data and data["top10"]:
    top10 = data["top10"]
    countries = top10.get("countries", [])
    values = top10.get("values", [])

    if len(countries) > 0 and len(values) > 0 and len(countries) == len(values):
        df_top10 = pd.DataFrame({"Country": countries, "Value": values})

        fig_top10 = px.bar(
            df_top10,
            x="Country",
            y="Value",
            title=top10.get("title", "Top 10 Countries"),
            labels={"Value": top_mode},
            text="Value"
        )
        fig_top10.update_traces(texttemplate="%{text:,}", textposition="outside")
        fig_top10.update_layout(height=500, title_x=0.5, margin={"r":0,"t":60,"l":0,"b":0})
        st.plotly_chart(fig_top10, use_container_width=True)
    else:
        st.warning("Dữ liệu top 10 không đầy đủ hoặc rỗng.")
else:
    st.warning("Backend chưa trả key 'top10' – có thể đang dùng code cũ hoặc lỗi đọc file.")