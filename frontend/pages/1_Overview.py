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
        params = {"mode": mode, "cache_buster": int(time.time() * 1000)}
        response = requests.get(DJANGO_API, params=params, timeout=15)
        response.raise_for_status()
        print("DEBUG RESPONSE:", response.json())
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
    options=[
        "Total Cases",
        "Total Deaths",
        "Death Rate (%)",
        "Infection Rate (%)"
    ],
    index=0,
    horizontal=True,
    key="trend_mode"
)

# ==================== DATAFRAME GỐC ====================
df_trends = pd.DataFrame({
    "Date": data["global_trends"]["dates"],
    "Total Cases": data["global_trends"]["cases"],
    "Total Deaths": data["global_trends"]["deaths"]
})

# ==================== XỬ LÝ THEO MODE ====================
if trend_mode == "Death Rate (%)":
    df_trends["Death Rate (%)"] = (
        df_trends["Total Deaths"] / df_trends["Total Cases"]
    ) * 100

    df_trends = df_trends.replace([float("inf"), -float("inf")], None)
    y_col = "Death Rate (%)"

elif trend_mode == "Infection Rate (%)":
    # population CHƯA CÓ → báo rõ ràng
    st.warning("❗ Infection Rate cần dữ liệu population (hiện API chưa cung cấp).")
    st.stop()

else:
    y_col = trend_mode

# ==================== VẼ BIỂU ĐỒ ====================
fig_trend = px.line(
    df_trends,
    x="Date",
    y=y_col,
    title=f"Xu hướng {trend_mode.lower()} toàn cầu"
)

# Format trục Y cho %
if "%" in trend_mode:
    fig_trend.update_yaxes(ticksuffix="%")

fig_trend.update_layout(
    height=450,
    title_x=0.5,
    title_font_size=22,
    margin={"r": 0, "t": 60, "l": 0, "b": 0},
    xaxis_title="Thời gian",
    yaxis_title=trend_mode
)

st.plotly_chart(fig_trend, use_container_width=True)

# ==================== TOP 10 QUỐC GIA (CHỈ COUNTRY THẬT) ====================
st.markdown("---")
st.subheader("🏆 Top 10 quốc gia bị ảnh hưởng nặng nhất")

top_mode = st.radio(
    "Chọn loại dữ liệu:",
    options=["Total Cases", "Total Deaths"],
    index=0,
    horizontal=True,
    key="top10_mode"
)

# ==================== LOAD DATA THEO MODE ====================
if top_mode == "Total Deaths":
    top_data = load_world_map_data("deaths")
else:
    top_data = data  # dùng lại data đã load cho cases

# ==================== TẠO DATAFRAME ====================
df_all = pd.DataFrame({
    "Country": top_data["locations"],
    "Value": top_data["values"]
})

# ==================== LỌC BỎ REGION / GROUP ====================
EXCLUDE_KEYWORDS = [
    "income",
    "world",
    "union",
    "countries",
    "africa",
    "europe",
    "asia",
    "america",
    "oceania"
]

df_all = df_all[
    ~df_all["Country"].str.contains(
        "|".join(EXCLUDE_KEYWORDS),
        case=False,
        na=False
    )
]

# ==================== LẤY TOP 10 ====================
df_top10 = (
    df_all
    .dropna()
    .sort_values("Value", ascending=False)
    .head(10)
)

# ==================== VẼ BIỂU ĐỒ ====================
if not df_top10.empty:
    fig_top10 = px.bar(
        df_top10,
        x="Country",
        y="Value",
        text="Value",
        title=f"Top 10 quốc gia theo {top_mode.lower()}",
        labels={"Value": top_mode},
        color="Value",
        color_continuous_scale="Reds" if top_mode == "Total Cases" else "Blues"
    )

    fig_top10.update_traces(
        texttemplate="%{text:,}",
        textposition="outside"
    )

    fig_top10.update_layout(
        height=520,
        title_x=0.5,
        title_font_size=22,
        margin={"r": 0, "t": 60, "l": 0, "b": 0},
        xaxis_tickangle=-30,
        yaxis_title=top_mode
    )

    st.plotly_chart(fig_top10, use_container_width=True)
else:
    st.warning("Không có dữ liệu Top 10.")






