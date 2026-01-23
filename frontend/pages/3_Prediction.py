import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from datetime import datetime
from style import set_custom_css

st.set_page_config(page_title="Dự báo Prophet COVID-19", page_icon="🔮", layout="wide")
set_custom_css()

# --- CẤU HÌNH URL ---
API_BASE_ANALYSIS = "http://localhost:8000/api/analysis"
API_PROPHET_URL = "http://localhost:8000/api/forecast/prophet-predict/"
API_ARIMA_URL   = "http://localhost:8000/api/forecast/arima-predict/"   # <-- THÊM MỚI

# --- HÀM HỖ TRỢ GỌI API ---
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
    url = f"{API_BASE_ANALYSIS}/world-map/?mode=deaths"
    data = fetch_data(url)
    if not data: return ["Vietnam"]
    df = pd.DataFrame(data)
    return sorted(df['location'].unique().tolist())

# --- SIDEBAR: ĐIỀU KHIỂN ---
st.sidebar.header("⚙️ Cấu hình dự báo")
country_list = get_all_locations()
selected_country = st.sidebar.selectbox("📍 Chọn quốc gia", country_list,
                                        index=country_list.index("Vietnam") if "Vietnam" in country_list else 0)

selected_date = st.sidebar.date_input("📅 Ngày bắt đầu so sánh", value=datetime(2022, 1, 1))
forecast_days = st.sidebar.selectbox("⏱️ Số ngày dự báo", [7, 14, 30, 60, 90], index=2)

st.sidebar.markdown("---")
st.sidebar.subheader("🛡️ Giả lập chính sách")
stringency_val = st.sidebar.slider(
    "Mức độ phong tỏa (%)",
    0, 100, 50,
    help="Kéo để thay đổi kịch bản: 0% là mở cửa, 100% là thiết quân luật."
)

predict_btn = st.sidebar.button("🚀 Chạy giả lập & Dự báo", use_container_width=True)

# --- GIAO DIỆN CHÍNH ---
st.title("🔮 Trình mô phỏng tác động chính sách COVID-19")
st.markdown(f"Đang phân tích kịch bản tại: **{selected_country}**")

# =========================
#     THÊM MỚI: TABS
# =========================
tab_prophet, tab_arima = st.tabs(["Prophet", "ARIMA"])  # <-- THÊM MỚI

# -------------------------
# TAB 1: PROPHET (GIỮ NGUYÊN)
# -------------------------
with tab_prophet:
    if predict_btn:
        params = {
            "location": selected_country,
            "start_date": str(selected_date),
            "days": forecast_days,
            "stringency_level": stringency_val
        }

        with st.spinner("🧠 AI đang tính toán kịch bản dựa trên dữ liệu thực tế..."):
            json_res = fetch_data(API_PROPHET_URL, params=params)

            if json_res and "predictions" in json_res:
                df_res = pd.DataFrame(json_res['predictions'])
                df_res['ds'] = pd.to_datetime(df_res['ds'])

                # Metadata
                mape = json_res['metadata'].get('mape')
                mae = json_res['metadata'].get('mae')

                # --- PHẦN 1: ĐÁNH GIÁ ĐỘ CHÍNH XÁC & ĐỘ TIN CẬY ---
                st.markdown("### 📊 Đánh giá độ chính xác & Độ tin cậy")

                if mape is not None and mae is not None:
                    accuracy_pct = max(0, 100 - mape)

                    if mape < 10:
                        eval_text = "Rất cao (Excellent)"
                        eval_color = "#28a745"
                        st_func = st.success
                    elif mape < 20:
                        eval_text = "Tốt (Good)"
                        eval_color = "#007bff"
                        st_func = st.info
                    else:
                        eval_text = "Cần lưu ý (Low Accuracy)"
                        eval_color = "#dc3545"
                        st_func = st.warning

                    col_acc1, col_acc2, col_acc3 = st.columns(3)
                    with col_acc1:
                        st.markdown(f"**MAPE (Tỷ lệ sai số):**")
                        st.markdown(f"<h2 style='color:{eval_color};'>{mape:.2f}%</h2>", unsafe_allow_html=True)
                    with col_acc2:
                        st.markdown(f"**MAE (Sai số trung bình):**")
                        st.markdown(f"<h2>{mae:,.0f} ca</h2>", unsafe_allow_html=True)
                    with col_acc3:
                        st.markdown(f"**Độ tin cậy dự báo:**")
                        st.markdown(f"<h2 style='color:{eval_color};'>{accuracy_pct:.1f}%</h2>", unsafe_allow_html=True)

                    st.progress(accuracy_pct / 100)
                    st_func(
                        f"Phân tích: Mô hình đạt độ chính xác **{eval_text}**. Sai số trung bình mỗi ngày khoảng {mae:,.0f} ca."
                    )
                else:
                    st.warning("⚠️ Không đủ dữ liệu thực tế trong khoảng thời gian này để tính toán sai số (MAPE/MAE).")

                st.divider()

                # --- PHẦN 2: TÓM TẮT CHỈ SỐ ---
                st.markdown("### 📌 So sánh Chỉ số Thực tế & Dự báo")

                last_idx = -1
                actual_data = df_res.dropna(subset=['y_actual'])

                c1, c2, c3 = st.columns(3)
                with c1:
                    val_baseline = int(df_res['yhat_baseline'].iloc[last_idx])
                    st.metric("Dự báo Baseline", f"{val_baseline:,} ca", "Kỳ vọng thực tế")
                with c2:
                    val_scenario = int(df_res['yhat_scenario'].iloc[last_idx])
                    diff = val_scenario - val_baseline
                    st.metric("Dự báo Kịch bản", f"{val_scenario:,} ca", f"{diff:+,} ca", delta_color="inverse")
                with c3:
                    max_risk = int(df_res['baseline_upper'].max())
                    st.metric("Kịch bản rủi ro cao", f"{max_risk:,} ca", "Giới hạn trên thực tế")

                # --- PHẦN 3: BIỂU ĐỒ ---
                st.markdown("---")
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=pd.concat([df_res['ds'], df_res['ds'][::-1]]),
                    y=pd.concat([df_res['baseline_upper'], df_res['baseline_lower'][::-1]]),
                    fill='toself',
                    fillcolor='rgba(59, 130, 246, 0.1)',
                    line=dict(color='rgba(255,255,255,0)'),
                    name='Khoảng tin cậy (Baseline)',
                    hoverinfo="skip"
                ))
                if 'y_actual' in df_res.columns and df_res['y_actual'].notna().any():
                    fig.add_trace(go.Scatter(
                        x=df_res['ds'], y=df_res['y_actual'],
                        name="Dữ liệu thực tế",
                        mode='lines+markers',
                        line=dict(color='#ef4444', width=2, dash='dot')
                    ))
                fig.add_trace(go.Scatter(
                    x=df_res['ds'], y=df_res['yhat_baseline'],
                    name="Dự báo (Theo thực tế)",
                    mode='lines',
                    line=dict(color='#3b82f6', width=2.5)
                ))
                fig.add_trace(go.Scatter(
                    x=df_res['ds'], y=df_res['yhat_scenario'],
                    name=f"Kịch bản (Phong tỏa {stringency_val}%)",
                    mode='lines',
                    line=dict(color='#f59e0b', width=4)
                ))
                fig.update_layout(
                    title=f"So sánh các kịch bản lây nhiễm tại {selected_country}",
                    xaxis_title="Thời gian",
                    yaxis_title="Số ca nhiễm mới",
                    template="plotly_white",
                    hovermode="x unified",
                    height=600,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig, use_container_width=True)

                actual_str = json_res['metadata'].get('actual_stringency', 50)
                user_str = json_res['metadata'].get('applied_stringency')
                if user_str is None: user_str = actual_str

                st.markdown("### ⚖️ So sánh chính sách")
                col_s1, col_s2, col_s3 = st.columns([1, 2, 1])
                with col_s1:
                    st.metric("Thực tế lúc đó", f"{actual_str:.0f}%", help="Mức độ phong tỏa đã áp dụng trong lịch sử")
                with col_s2:
                    delta_val = user_str - actual_str
                    status_text = ("Nới lỏng " + f"{abs(delta_val):.0f}%") if delta_val < 0 else \
                                  ("Siết chặt thêm " + f"{delta_val:.0f}%") if delta_val > 0 else "Giữ nguyên"
                    st.metric("Bạn chọn", f"{user_str:.0f}%", f"{status_text}",
                              delta_color="normal" if delta_val > 0 else "inverse")
                with col_s3:
                    if diff > 0:
                        st.markdown(f"<span style='color:red; font-weight:bold; font-size: 20px'>↗ Tăng {abs(diff):,.0f} ca</span>", unsafe_allow_html=True)
                    elif diff < 0:
                        st.markdown(f"<span style='color:green; font-weight:bold; font-size: 20px'>↘ Giảm {abs(diff):,.0f} ca</span>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<span style='color:gray; font-weight:bold; font-size: 20px'>➖ Không đổi</span>", unsafe_allow_html=True)

                st.markdown("### 📝 Phân tích chi tiết")
                if diff > 0:
                    st.warning(
                        f"⚠️ **Cảnh báo:** Tại thời điểm dự báo, mức phong tỏa thực tế của quốc gia là **{actual_str:.0f}%**.\n\n"
                        f"Việc bạn chọn mức **{user_str:.0f}%** đồng nghĩa với việc **nới lỏng chính sách**, "
                        f"dẫn đến số ca nhiễm tăng thêm **{diff:,.0f} ca**."
                    )
                elif diff < 0:
                    st.success(
                        f"✅ **Hiệu quả:** Tại thời điểm dự báo, mức phong tỏa thực tế là **{actual_str:.0f}%**.\n\n"
                        f"Việc bạn nâng mức phong tỏa lên **{user_str:.0f}%** (siết chặt thêm) "
                        f"có thể giúp ngăn chặn được **{abs(diff):,.0f} ca nhiễm**."
                    )

                with st.expander("📂 Xem bảng dữ liệu chi tiết theo ngày"):
                    st.dataframe(df_res, use_container_width=True)
            else:
                st.error("❌ Không thể kết nối hoặc dữ liệu từ máy chủ bị rỗng.")
    else:
        st.divider()
        st.info("👈 Hãy thiết lập các tham số và nhấn nút chạy để bắt đầu giả lập kịch bản.")

# -------------------------
# TAB 2: ARIMA (CHỈ THÊM MỚI, KHÔNG ĐỤNG LOGIC PROPHET)
# -------------------------
with tab_arima:
    if predict_btn:
        params = {
            "location": selected_country,
            "start_date": str(selected_date),
            "days": forecast_days,
            "stringency_level": stringency_val
        }

        with st.spinner("📈 ARIMA đang tính toán dự báo..."):
            json_res = fetch_data(API_ARIMA_URL, params=params)

            if json_res and "predictions" in json_res:
                df_res = pd.DataFrame(json_res['predictions'])
                df_res['ds'] = pd.to_datetime(df_res['ds'])

                mape = json_res['metadata'].get('mape')
                mae = json_res['metadata'].get('mae')

                st.markdown("### 📊 Đánh giá độ chính xác & Độ tin cậy (ARIMA)")
                if mape is not None and mae is not None:
                    accuracy_pct = max(0, 100 - mape)
                    if mape < 10:
                        eval_text = "Rất cao (Excellent)"
                        eval_color = "#28a745"
                        st_func = st.success
                    elif mape < 20:
                        eval_text = "Tốt (Good)"
                        eval_color = "#007bff"
                        st_func = st.info
                    else:
                        eval_text = "Cần lưu ý (Low Accuracy)"
                        eval_color = "#dc3545"
                        st_func = st.warning

                    col_acc1, col_acc2, col_acc3 = st.columns(3)
                    with col_acc1:
                        st.markdown(f"**MAPE (Tỷ lệ sai số):**")
                        st.markdown(f"<h2 style='color:{eval_color};'>{mape:.2f}%</h2>", unsafe_allow_html=True)
                    with col_acc2:
                        st.markdown(f"**MAE (Sai số trung bình):**")
                        st.markdown(f"<h2>{mae:,.0f} ca</h2>", unsafe_allow_html=True)
                    with col_acc3:
                        st.markdown(f"**Độ tin cậy dự báo:**")
                        st.markdown(f"<h2 style='color:{eval_color};'>{accuracy_pct:.1f}%</h2>", unsafe_allow_html=True)

                    st.progress(accuracy_pct / 100)
                    st_func(
                        f"Phân tích: ARIMA đạt độ chính xác **{eval_text}**. Sai số trung bình mỗi ngày khoảng {mae:,.0f} ca."
                    )
                else:
                    st.warning("⚠️ Không đủ dữ liệu thực tế trong khoảng thời gian này để tính toán sai số (MAPE/MAE).")

                st.divider()

                st.markdown("### 📌 So sánh Chỉ số Thực tế & Dự báo (ARIMA)")
                last_idx = -1
                c1, c2, c3 = st.columns(3)
                with c1:
                    val_baseline = int(df_res['yhat_baseline'].iloc[last_idx])
                    st.metric("Dự báo Baseline", f"{val_baseline:,} ca", "Kỳ vọng thực tế")
                with c2:
                    val_scenario = int(df_res['yhat_scenario'].iloc[last_idx])
                    diff = val_scenario - val_baseline
                    st.metric("Dự báo Kịch bản", f"{val_scenario:,} ca", f"{diff:+,} ca", delta_color="inverse")
                with c3:
                    max_risk = int(df_res['baseline_upper'].max())
                    st.metric("Kịch bản rủi ro cao", f"{max_risk:,} ca", "Giới hạn trên thực tế")

                st.markdown("---")
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=pd.concat([df_res['ds'], df_res['ds'][::-1]]),
                    y=pd.concat([df_res['baseline_upper'], df_res['baseline_lower'][::-1]]),
                    fill='toself',
                    fillcolor='rgba(34, 197, 94, 0.12)',  # xanh lá nhạt để phân biệt Prophet
                    line=dict(color='rgba(255,255,255,0)'),
                    name='Khoảng tin cậy (Baseline)',
                    hoverinfo="skip"
                ))
                if 'y_actual' in df_res.columns and df_res['y_actual'].notna().any():
                    fig.add_trace(go.Scatter(
                        x=df_res['ds'], y=df_res['y_actual'],
                        name="Dữ liệu thực tế",
                        mode='lines+markers',
                        line=dict(color='#ef4444', width=2, dash='dot')
                    ))
                fig.add_trace(go.Scatter(
                    x=df_res['ds'], y=df_res['yhat_baseline'],
                    name="Dự báo (ARIMA)",
                    mode='lines',
                    line=dict(color='#22c55e', width=2.5)  # xanh lá
                ))
                fig.add_trace(go.Scatter(
                    x=df_res['ds'], y=df_res['yhat_scenario'],
                    name=f"Kịch bản (Phong tỏa {stringency_val}%)",
                    mode='lines',
                    line=dict(color='#f59e0b', width=4)
                ))
                fig.update_layout(
                    title=f"Biểu đồ đối chiếu ARIMA tại {selected_country}",
                    xaxis_title="Thời gian",
                    yaxis_title="Số ca nhiễm mới",
                    template="plotly_white",
                    hovermode="x unified",
                    height=600,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig, use_container_width=True)

                actual_str = json_res['metadata'].get('actual_stringency', 50)
                user_str = json_res['metadata'].get('applied_stringency')
                if user_str is None: user_str = actual_str

                st.markdown("### ⚖️ So sánh chính sách (ARIMA)")
                col_s1, col_s2, col_s3 = st.columns([1, 2, 1])
                with col_s1:
                    st.metric("Thực tế lúc đó", f"{actual_str:.0f}%")
                with col_s2:
                    delta_val = user_str - actual_str
                    status_text = ("Nới lỏng " + f"{abs(delta_val):.0f}%") if delta_val < 0 else \
                                  ("Siết chặt thêm " + f"{delta_val:.0f}%") if delta_val > 0 else "Giữ nguyên"
                    st.metric("Bạn chọn", f"{user_str:.0f}%", f"{status_text}",
                              delta_color="normal" if delta_val > 0 else "inverse")
                with col_s3:
                    if diff > 0:
                        st.markdown(f"<span style='color:red; font-weight:bold; font-size: 20px'>↗ Tăng {abs(diff):,.0f} ca</span>", unsafe_allow_html=True)
                    elif diff < 0:
                        st.markdown(f"<span style='color:green; font-weight:bold; font-size: 20px'>↘ Giảm {abs(diff):,.0f} ca</span>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<span style='color:gray; font-weight:bold; font-size: 20px'>➖ Không đổi</span>", unsafe_allow_html=True)

                with st.expander("📂 Xem bảng dữ liệu chi tiết theo ngày (ARIMA)"):
                    st.dataframe(df_res, use_container_width=True)
            else:
                st.error("❌ Không thể kết nối hoặc dữ liệu từ máy chủ bị rỗng.")
    else:
        st.divider()
        st.info("👈 Chọn tham số và nhấn nút chạy để xem dự báo ARIMA.")
