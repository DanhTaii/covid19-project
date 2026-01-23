import streamlit as st
import requests
import plotly.express as px
import pandas as pd
import importlib.util
from style import set_custom_css  # nếu tách file

# GỌI CSS TRƯỚC
set_custom_css()

# CẤU HÌNH TRANG
st.set_page_config(
    page_title="Phân Tích Chuyên Sâu COVID-19",
    page_icon="🔎",
    layout="wide"
)

# KIỂM TRA THƯ VIỆN BỔ TRỢ
has_statsmodels = importlib.util.find_spec("statsmodels") is not None

# CSS TÙY CHỈNH
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        border-left: 5px solid #ff4b4b;
        border-radius: 5px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .big-stat {
        font-size: 24px;
        font-weight: bold;
        color: #31333F;
    }
    .sub-stat {
        font-size: 14px;
        color: #666;
    }
</style>
""", unsafe_allow_html=True)

# CẤU HÌNH API ENDPOINTS CHÍNH
API_BASE = "http://localhost:8000/api/analysis"


# HÀM GỌI API
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_data(url, params=None):
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Lỗi kết nối API: {e}")
        return None


# Trong file 2_Insight.py

@st.cache_data(ttl=3600)
def get_all_locations():
    """Lấy danh sách quốc gia từ API Map"""
    url = f"{API_BASE}/world-map/?mode=deaths"
    data = fetch_data(url)

    # Nếu lỗi hoặc rỗng thì trả về danh sách trống hoặc 1 nước mặc định
    if not data:
        return []

    df = pd.DataFrame(data)

    if 'location' not in df.columns:
        return []

    # Lấy danh sách quốc gia và sắp xếp
    countries = sorted(df['location'].astype(str).unique().tolist())

    # --- THAY ĐỔI Ở ĐÂY: Trả về trực tiếp countries, KHÔNG cộng thêm ['All Countries'] ---
    return countries


# GIAO DIỆN CHÍNH

st.title("🔎 Phân Tích Chuyên Sâu: Nghiêm Trọng & Nguyên Nhân")
st.markdown("---")

# --- SIDEBAR: LỌC QUỐC GIA ---
st.sidebar.header("⚙️ Bộ Lọc")

country_list = get_all_locations()

# Tìm vị trí của Vietnam trong danh sách để set mặc định
default_index = 0
if "Vietnam" in country_list:
    default_index = country_list.index("Vietnam")

# Selectbox
selected_country = st.sidebar.selectbox(
    "Chọn Quốc gia",
    country_list,
    index=default_index  # Mặc định chọn Vietnam (hoặc nước đầu tiên nếu không có VN)
)

st.sidebar.info(f"Đang xem dữ liệu: **{selected_country}**")

# TABS
tab_insight1, tab_insight2, tab_insight3, tab_insight4 = st.tabs([
    "📊 Insight 1: Tổng quan Quốc gia",
    " Insight 2: Mức độ lây lan",
    "🗺️ Insight 3: Mức Độ Nghiêm Trọng",
    "🧬 Insight 4: Yếu Tố Rủi Ro"
])

# ==============================================================================
#                               INSIGHT 1 LOGIC
# ==============================================================================
with tab_insight1:
    st.subheader(f"📊 Tổng quan COVID-19 tại: {selected_country}")

    api_insight1_url = f"{API_BASE}/country-overview/"
    params = {"location": selected_country}
    res_data = fetch_data(api_insight1_url, params=params)

    if res_data and 'data' in res_data:
        summary = res_data['data']
    elif res_data:  # nếu backend trả thẳng dict (không bọc data)
        summary = res_data
    else:
        summary = None

    if summary:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Tổng ca nhiễm", f"{summary.get('total_cases', 0):,}")
        with col2:
            st.metric("Tổng ca tử vong", f"{summary.get('total_deaths', 0):,}")
        with col3:
            st.metric("Tỉ lệ tử vong", f"{summary.get('mortality_rate', 0):.2f} %")
        with col4:
            st.metric("Tỉ lệ tiêm chủng", f"{summary.get('vaccination_rate', 0):.2f} %")
    else:
        st.warning(f"Không có dữ liệu cho {selected_country}")

# ==============================================================================
#                               INSIGHT 2: Transmission Rate
# ==============================================================================

with tab_insight2:
    st.subheader(f"📈 Mức độ Lây lan tại: {selected_country}")

    # 1. Gọi API lấy dữ liệu lịch sử lây lan
    api_insight2_url = f"{API_BASE}/transmission-rate/"
    params = {"location": selected_country}
    res_data = fetch_data(api_insight2_url, params=params)

    if res_data:
        df_trend = pd.DataFrame(res_data)

        # BIỂU ĐỒ ĐƯỜNG: Diễn biến ca mắc mới
        if not df_trend.empty:
            fig_line = px.line(
                df_trend,
                x='date',
                y='new_cases_smoothed_per_million',
                title=f"Tốc độ lây nhiễm trên 1 triệu dân",
                template="plotly_white"
            )

            fig_line.update_traces(line_color='#ff4b4b')
            st.plotly_chart(fig_line, use_container_width=True)
            st.info(
                "💡 **Ghi chú:** Chỉ số 'Smooth' là trung bình trượt 7 ngày để giảm nhiễu dữ liệu do báo cáo chậm vào cuối tuần.")
        else:
            st.warning(f"Không tìm thấy dữ liệu xu hướng cho {selected_country}")
    else:
        st.warning(f"Không có dữ liệu lây lan cho {selected_country}")

# ==============================================================================
#                               INSIGHT 3 LOGIC
# ==============================================================================
with tab_insight3:
    st.subheader(f"📍 Tình hình Tử vong tại: {selected_country}")

    # Gọi API
    api_insight3_url = f"{API_BASE}/mortality-ratio/"
    params = {'location': selected_country}  # Luôn gửi tên quốc gia lên

    res_data = fetch_data(api_insight3_url, params=params)

    if res_data:
        stat = res_data.get('statistic', {})
        map_data = res_data.get('map_data', [])

        # 1. Hiển thị số liệu
        if stat:
            st.markdown(f"""
            <div class="metric-card">
                <div class="sub-stat">{stat.get('label', 'Tỷ lệ tử vong')}</div>
                <div class="big-stat">{stat.get('value', '0')} <span style="font-size:16px; color:#666">trên 1 triệu dân</span></div>
                <div class="sub-stat">Khu vực: {stat.get('location', selected_country)}</div>
            </div>
            """, unsafe_allow_html=True)

        # 2. Hiển thị Bản đồ
        if map_data:
            df_map = pd.DataFrame(map_data)

            fig_map = px.choropleth(
                df_map,
                locations="iso_code",
                color="total_deaths_per_million",
                hover_name="location",
                color_continuous_scale="Reds",
                title=f"Vị trí của {selected_country} trên bản đồ",
            )

            # Chỉ hiện khung bản đồ thế giới, tô màu nước được chọn
            fig_map.update_geos(
                showframe=False,
                showcoastlines=True,
                projection_type="natural earth",
                showcountries=True,
                countrycolor="#d1d1d1",  # Màu viền các nước khác
                showland=True,
                landcolor="#f0f2f6"  # Màu nền các nước không được chọn (xám nhạt)
            )

            # Tắt thanh màu bên cạnh (Legend) vì chỉ có 1 nước thì không cần so sánh màu
            fig_map.update_layout(height=500, margin={"r": 0, "t": 30, "l": 0, "b": 0}, coloraxis_showscale=False)

            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.warning(f"Chưa có dữ liệu bản đồ cho {selected_country}")

# ==============================================================================
#                               INSIGHT 4 LOGIC
# ==============================================================================
with tab_insight4:
    st.subheader("🔗 Mối tương quan: Yếu Tố Rủi Ro vs. Tỷ lệ Tử vong")
    st.info("💡 Insight này luôn sử dụng dữ liệu **Toàn cầu (Global)** để tính toán xu hướng thống kê chính xác nhất.")

    # Luôn gọi API với location='All Countries' hoặc continent='World' để có đủ dữ liệu vẽ biểu đồ scatter
    api_corr_url = f"{API_BASE}/factor-correlation/"
    # Không truyền params filter để lấy full data
    corr_data = fetch_data(api_corr_url)

    if corr_data:
        correlation_matrix = corr_data.get('correlation_matrix', {})
        scatter_data = corr_data.get('scatter_data', {})

        # 1. Heatmap
        if correlation_matrix:
            df_corr = pd.DataFrame(correlation_matrix)

            # Đổi tên cột cho đẹp
            rename_map = {
                'total_deaths_per_million': 'Tử vong',
                'median_age': 'Tuổi trung bình',
                'population_density': 'Mật độ dân',
                'total_vaccinations_per_hundred': 'Vắc-xin'
            }
            df_corr = df_corr.rename(index=rename_map, columns=rename_map)

            fig_heatmap = px.imshow(
                df_corr,
                text_auto=".2f",
                aspect="auto",
                color_continuous_scale="RdBu_r",
                origin='lower'
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)

        st.divider()

        # 2. Scatter Plots
        st.markdown("### 📊 Chi tiết phân tán")
        col1, col2 = st.columns(2)
        trendline = "ols" if has_statsmodels else None

        # Biểu đồ Tuổi
        with col1:
            st.markdown("**Tuổi tác vs. Tử vong**")
            if scatter_data.get('age_vs_deaths'):
                df_age = pd.DataFrame(scatter_data['age_vs_deaths'])

                # Tạo cột màu: Nếu quốc gia đang chọn trùng với dòng dữ liệu -> Màu đỏ, còn lại màu xanh
                df_age['color_type'] = df_age['location'].apply(
                    lambda x: 'Selected' if x == selected_country else 'Others'
                )

                # Màu sắc
                color_map = {'Selected': 'red', 'Others': 'blue'}

                fig_age = px.scatter(
                    df_age,
                    x="median_age",
                    y="total_deaths_per_million",
                    hover_name="location",
                    color='color_type',
                    color_discrete_map=color_map,
                    trendline=trendline if selected_country == 'All Countries' else None,
                    # Chỉ vẽ trendline khi xem tất cả
                    labels={"median_age": "Tuổi trung bình", "total_deaths_per_million": "Tử vong/1M dân"}
                )
                fig_age.update_layout(showlegend=False)
                st.plotly_chart(fig_age, use_container_width=True)

        # Biểu đồ Vắc-xin
        with col2:
            st.markdown("**Vắc-xin vs. Tử vong**")
            if scatter_data.get('vaccine_vs_deaths'):
                df_vac = pd.DataFrame(scatter_data['vaccine_vs_deaths'])

                # Highlight quốc gia đang chọn
                df_vac['color_type'] = df_vac['location'].apply(
                    lambda x: 'Selected' if x == selected_country else 'Others'
                )

                color_map = {'Selected': 'red', 'Others': 'green'}

                fig_vac = px.scatter(
                    df_vac,
                    x="total_vaccinations_per_hundred",
                    y="total_deaths_per_million",
                    hover_name="location",
                    color='color_type',
                    color_discrete_map=color_map,
                    trendline=trendline if selected_country == 'All Countries' else None,
                    labels={"total_vaccinations_per_hundred": "Liều Vắc-xin/100 dân",
                            "total_deaths_per_million": "Tử vong/1M dân"}
                )
                fig_vac.update_layout(showlegend=False)
                st.plotly_chart(fig_vac, use_container_width=True)

        if selected_country != 'All Countries':
            st.caption(f"🔴 Điểm màu đỏ trên biểu đồ là vị trí của **{selected_country}** so với thế giới.")

    else:
        st.error("Không thể tải dữ liệu Insight 4.")
