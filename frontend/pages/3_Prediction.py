import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from datetime import datetime
from style import set_custom_css

st.set_page_config(page_title="Dự báo Prophet COVID-19", page_icon="🔮", layout="wide")
set_custom_css()

# --- CẤU HÌNH URL (Đảm bảo khớp với urls.py của Django) ---
API_BASE_ANALYSIS = "http://localhost:8000/api/analysis"
# Lưu ý: Kiểm tra lại endpoint này có khớp với đường dẫn trong urls.py không
API_PROPHET_URL = "http://localhost:8000/api/forecast/prophet-predict/"


# 2. HÀM HỖ TRỢ GỌI API
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_data(url, params=None):
    try:
        response = requests.get(url, params=params, timeout=25)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Lỗi kết nối API: {e}")
        return None


@st.cache_data(ttl=3600)
def get_all_locations():
    """Lấy danh sách quốc gia động"""
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

selected_date = st.sidebar.date_input("📅 Ngày bắt đầu so sánh/dự báo", value=datetime(2022, 1, 1))
forecast_days = st.sidebar.selectbox("⏱️ Số ngày dự báo", [7, 14, 30, 60, 90], index=2)

predict_btn = st.sidebar.button("🚀 Chạy phân tích & Dự báo", use_container_width=True)

# 4. GIAO DIỆN CHÍNH
st.title("🔮 Dự báo & Kiểm chứng xu hướng COVID-19")
st.markdown(f"Đang phân tích dữ liệu tại: **{selected_country}**")

if predict_btn:
    params = {
        "location": selected_country,
        "start_date": str(selected_date),
        "days": forecast_days
    }

    with st.spinner("🧠 Hệ thống đang xử lý dữ liệu thực tế và tính toán dự báo..."):
        json_res = fetch_data(API_PROPHET_URL, params=params)

        if json_res and "predictions" in json_res:

            mape = json_res['metadata'].get('mape')

            # Hiển thị đánh giá mô hình
            st.markdown("### 📊 Đánh giá độ chính xác")
            if mape is not None:
                # Chọn màu sắc dựa trên độ lỗi
                color = "green" if mape < 10 else "orange" if mape < 20 else "red"
                st.markdown(
                    f"Sai số trung bình (MAPE): <span style='color:{color}; font-size:24px; font-weight:bold;'>{mape:.2f}%</span>",
                    unsafe_allow_html=True)

                # Giải thích ý nghĩa
                if mape < 10:
                    st.success("✅ Mô hình có độ chính xác rất cao!")
                elif mape < 20:
                    st.info("ℹ️ Mô hình có độ chính xác tốt.")
                else:
                    st.warning("⚠️ Mô hình có sai số khá lớn, hãy cân nhắc điều chỉnh tham số.")
            else:
                st.write("Không đủ dữ liệu thực tế để tính toán sai số.")

            # Chuyển dữ liệu JSON thành DataFrame
            df_res = pd.DataFrame(json_res['predictions'])
            df_res['ds'] = pd.to_datetime(df_res['ds'])

            # --- PHẦN 1: TÓM TẮT KẾT QUẢ (METRIC CARDS) ---
            st.markdown("### 📌 So sánh Chỉ số Thực tế & Dự báo")

            # Tính toán các con số tóm tắt
            last_row = df_res.iloc[-1]
            # Lấy giá trị thực tế cuối cùng có dữ liệu (tránh ngày chưa xảy ra)
            actual_data = df_res.dropna(subset=['y_actual'])

            c1, c2, c3 = st.columns(3)

            with c1:
                val = int(last_row['yhat'])
                st.metric("Dự báo cuối kỳ", f"{val:,} ca", "Kỳ vọng")

            with c2:
                if not actual_data.empty:
                    last_actual = int(actual_data['y_actual'].iloc[-1])
                    diff = last_actual - int(actual_data['yhat'].iloc[-1])
                    st.metric("Thực tế cuối kỳ", f"{last_actual:,} ca", f"{diff:+} so với dự báo")
                else:
                    st.metric("Thực tế cuối kỳ", "N/A", "Không có dữ liệu")

            with c3:
                max_upper = int(df_res['yhat_upper'].max())
                st.metric("Kịch bản rủi ro cao", f"{max_upper:,} ca", "Giới hạn trên")

            # --- PHẦN 2: BIỂU ĐỒ SO SÁNH CHI TIẾT ---
            st.markdown("---")
            fig = go.Figure()

            # A. Vẽ vùng tin cậy (Confidence Interval)
            fig.add_trace(go.Scatter(
                x=pd.concat([df_res['ds'], df_res['ds'][::-1]]),
                y=pd.concat([df_res['yhat_upper'], df_res['yhat_lower'][::-1]]),
                fill='toself',
                fillcolor='rgba(30, 58, 138, 0.1)',
                line=dict(color='rgba(255,255,255,0)'),
                name='Khoảng tin cậy (80%)',
                hoverinfo="skip"
            ))

            # B. Vẽ đường dự báo (Yhat)
            fig.add_trace(go.Scatter(
                x=df_res['ds'],
                y=df_res['yhat'],
                mode='lines+markers',
                line=dict(color='#1e3a8a', width=3),
                marker=dict(size=4),
                name='Mô hình dự báo'
            ))

            # C. Vẽ đường thực tế (Actual)
            if 'y_actual' in df_res.columns:
                fig.add_trace(go.Scatter(
                    x=df_res['ds'],
                    y=df_res['y_actual'],
                    mode='lines+markers',
                    line=dict(color='#ef4444', width=2, dash='dot'),
                    marker=dict(size=6, symbol='circle-open'),
                    name='Dữ liệu thực tế (Đối chứng)'
                ))

            fig.update_layout(
                title=f"Biểu đồ đối chiếu tại {selected_country} (từ {selected_date})",
                xaxis_title="Thời gian",
                yaxis_title="Số ca nhiễm mới",
                template="plotly_white",
                hovermode="x unified",
                height=550,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )

            st.plotly_chart(fig, use_container_width=True)

            # --- PHẦN 3: BẢNG DỮ LIỆU CHI TIẾT ---
            with st.expander("📂 Xem bảng dữ liệu chi tiết"):
                st.dataframe(df_res, use_container_width=True)

        else:
            st.error("⚠️ Không nhận được dữ liệu từ máy chủ. Hãy kiểm tra URL hoặc Backend.")

else:
    st.divider()
    st.info("👈 Hãy thiết lập các tham số bên trái và nhấn 'Chạy dự báo' để xem kết quả đối chiếu.")
    st.image("https://img.freepik.com/free-vector/predictive-analytics-concept-illustration_114360-7117.jpg", width=600)