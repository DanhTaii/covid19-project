import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from datetime import datetime
from style import set_custom_css

# 1. KHỞI TẠO GIAO DIỆN
st.set_page_config(page_title="Dự báo Prophet COVID-19", page_icon="🔮", layout="wide")
set_custom_css()

# --- CẤU HÌNH URL ---
API_BASE_ANALYSIS = "http://localhost:8000/api/analysis"
API_PROPHET_URL = "http://localhost:8000/api/forecast/prophet-predict/"


# 2. HÀM HỖ TRỢ GỌI API
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_data(url, params=None):
    try:
        response = requests.get(url, params=params, timeout=25)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return None


@st.cache_data(ttl=3600)
def get_all_locations():
    """Lấy danh sách quốc gia động từ API giống Insight"""
    url = f"{API_BASE_ANALYSIS}/world-map/?mode=deaths"
    data = fetch_data(url)
    if not data:
        return ["Vietnam"]
    df = pd.DataFrame(data)
    if 'location' not in df.columns:
        return ["Vietnam"]
    return sorted(df['location'].astype(str).unique().tolist())


# 3. GIAO DIỆN SIDEBAR
st.sidebar.header("⚙️ Cấu hình dự báo")

country_list = get_all_locations()
default_index = country_list.index("Vietnam") if "Vietnam" in country_list else 0

selected_country = st.sidebar.selectbox("📍 Chọn quốc gia", country_list, index=default_index)

st.sidebar.markdown("---")

selected_date = st.sidebar.date_input("📅 Ngày bắt đầu dự báo", value=datetime(2022, 1, 1))

# ĐÃ LOẠI BỎ SLIDER STRINGENCY TẠI ĐÂY

forecast_days = st.sidebar.selectbox("⏱️ Số ngày dự báo", [7, 14, 30, 60, 90], index=2)

predict_btn = st.sidebar.button("🚀 Chạy dự báo ngay", use_container_width=True)

# 4. GIAO DIỆN CHÍNH
st.title("🔮 Dự báo xu hướng COVID-19")
st.markdown(f"Dự báo dựa trên dữ liệu lịch sử tại: **{selected_country}**")

if predict_btn:
    # ĐÃ LOẠI BỎ STRINGENCY KHỎI PARAMS
    params = {
        "location": selected_country,
        "start_date": str(selected_date),
        "days": forecast_days
    }

    with st.spinner("🧠 Đang phân tích xu hướng và tính toán..."):
        json_res = fetch_data(API_PROPHET_URL, params=params)

        if json_res and "predictions" in json_res:
            df_res = pd.DataFrame(json_res['predictions'])
            df_res['ds'] = pd.to_datetime(df_res['ds'])

            # --- PHẦN 1: TÓM TẮT KẾT QUẢ (METRIC CARDS) ---
            st.markdown("### 📌 Tóm tắt kết quả dự báo")
            # Chia làm 2 cột vì đã bỏ cột Stringency
            c1, c2 = st.columns(2)

            final_yhat = df_res['yhat'].iloc[-1]
            max_risk = df_res['yhat_upper'].max()

            with c1:
                st.markdown(f"""
                <div class="metric-card" style="border-left-color: #1e3a8a;">
                    <div class="sub-stat">Dự báo sau {forecast_days} ngày</div>
                    <div class="big-stat">{int(final_yhat):,} <span style="font-size:14px">ca/ngày</span></div>
                    <div class="sub-stat">Giá trị kỳ vọng (yhat)</div>
                </div>
                """, unsafe_allow_html=True)

            with c2:
                st.markdown(f"""
                <div class="metric-card" style="border-left-color: #ef4444;">
                    <div class="sub-stat">Kịch bản rủi ro tối đa</div>
                    <div class="big-stat">{int(max_risk):,} <span style="font-size:14px">ca/ngày</span></div>
                    <div class="sub-stat">Giới hạn trên (yhat_upper)</div>
                </div>
                """, unsafe_allow_html=True)

            # --- PHẦN 2: BIỂU ĐỒ CHI TIẾT (PLOTLY) ---
            st.markdown("---")
            fig = go.Figure()

            # Vẽ vùng tin cậy
            fig.add_trace(go.Scatter(
                x=pd.concat([df_res['ds'], df_res['ds'][::-1]]),
                y=pd.concat([df_res['yhat_upper'], df_res['yhat_lower'][::-1]]),
                fill='toself',
                fillcolor='rgba(30, 58, 138, 0.1)',
                line=dict(color='rgba(255,255,255,0)'),
                name='Khoảng tin cậy (80%)',
                hoverinfo="skip"
            ))

            # Vẽ đường dự báo
            fig.add_trace(go.Scatter(
                x=df_res['ds'],
                y=df_res['yhat'],
                mode='lines+markers',
                line=dict(color='#1e3a8a', width=3),
                marker=dict(size=4),
                name='Số ca dự báo'
            ))

            fig.update_layout(
                title=f"Biểu đồ xu hướng tại {selected_country} (Khởi đầu từ {selected_date})",
                xaxis_title="Thời gian",
                yaxis_title="Số ca nhiễm (Dự báo)",
                template="plotly_white",
                hovermode="x unified",
                height=500,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )

            st.plotly_chart(fig, use_container_width=True)

            # ĐÃ LOẠI BỎ PHẦN INFO GHI CHÚ VỀ STRINGENCY Ở ĐÂY

        else:
            st.error("⚠️ Không nhận được dữ liệu từ máy chủ. Hãy kiểm tra Backend của bạn.")

else:
    st.divider()
    st.info("👈 Hãy thiết lập các tham số bên trái và nhấn 'Chạy dự báo' để xem kết quả.")
    st.image("https://img.freepik.com/free-vector/predictive-analytics-concept-illustration_114360-7117.jpg", width=600)