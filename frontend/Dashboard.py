import streamlit as st
from streamlit import sidebar
from style import set_custom_css  # nếu tách file
import requests
# GỌI CSS TRƯỚC
set_custom_css()

st.set_page_config(page_title="COVID-19 Analysis System", layout="wide", page_icon="image/logo.jpg")

st.title("COVID-19 Dashboard 🦠")
st.write("Welcome to the COVID-19 analysis system!")

sidebar.title("COVID-19 Analysis System")
selected_tab = st.sidebar.radio("Select Tab", ["Home", "About"])
#
# import streamlit as st
# import pandas as pd
# import datetime
#
# st.set_page_config(layout="wide")  # Đặt bố cục trang thành "rộng"
#
# API_BASE = "http://localhost:8000/api/analysis"
#
# # ==================== HÀM GỌI API ====================
# @st.cache_data(ttl=3600, show_spinner=False)
# def fetch_data(url, params=None):
#     try:
#         response = requests.get(url, params=params, timeout=15)
#         response.raise_for_status()
#         return response.json()
#     except requests.exceptions.RequestException as e:
#         st.error(f"❌ Lỗi kết nối API: {e}")
#         return None
#
# @st.cache_data(ttl=3600)
# def get_all_locations():
#     """Lấy danh sách quốc gia từ API Map"""
#     url = f"{API_BASE}/world-map/?mode=deaths"
#     data = fetch_data(url)
#
#     # Nếu lỗi hoặc rỗng thì trả về danh sách trống hoặc 1 nước mặc định
#     if not data:
#         return []
#
#     df = pd.DataFrame(data)
#
#     if 'location' not in df.columns:
#         return []
#
#     # Lấy danh sách quốc gia và sắp xếp
#     countries = sorted(df['location'].astype(str).unique().tolist())
#
#     # --- THAY ĐỔI Ở ĐÂY: Trả về trực tiếp countries, KHÔNG cộng thêm ['All Countries'] ---
#     return countries
#
# # --- 2. Cột Tiêu đề Chính ---
# st.title('🌍 Phân tích & So sánh Dữ liệu COVID-19')
# st.markdown('Sử dụng thanh bên để lựa chọn các tiêu chí phân tích.')
#
# # --- 3. Thanh Bên (Sidebar) - Chứa các Widget Tùy chọn ---
# st.sidebar.header('⚙️ Cài đặt & Lựa chọn')
#
# # Widget 1: Chọn Quốc gia
# quoc_gia_da_chon = st.sidebar.multiselect(
#     'Chọn các Quốc gia để So sánh',
#     options=get_all_locations(),
#     default=['Vietnam', 'United States']
# )
#
# # Widget 2: Chọn Chỉ số (Biến số)
# cac_chi_so = ['total_cases', 'new_deaths', 'hospital_patients', 'stringency_index']
# chi_so_da_chon = st.sidebar.selectbox(
#     'Chọn Chỉ số để Trực quan hóa',
#     options=cac_chi_so
# )
#
# # Widget 3: Tùy chọn Thang đo
# su_dung_log_scale = st.sidebar.checkbox(
#     'Sử dụng Thang đo Logarit (Log Scale)',
#     value=False
# )
#
# # Widget 4: Phạm vi Ngày (Giả định)
# ngay_bat_dau_min = datetime.date(2020, 1, 1)
# ngay_ket_thuc_max = datetime.date.today()
# pham_vi_ngay = st.sidebar.date_input(
#     'Chọn Phạm vi Ngày',
#     value=(ngay_bat_dau_min, ngay_ket_thuc_max),
#     min_value=ngay_bat_dau_min,
#     max_value=ngay_ket_thuc_max
# )
#
# # --- 4. Nội dung Chính (Main Content) ---
#
# if not quoc_gia_da_chon:
#     st.info('Vui lòng chọn ít nhất một quốc gia từ thanh bên để bắt đầu phân tích.')
# else:
#     # Ứng dụng các lựa chọn để lọc data (Phần này là trọng tâm của bạn)
#
#     st.subheader(f'Đồ thị Biến động **{chi_so_da_chon.replace("_", " ").title()}**')
#
#     # 💡 Gợi ý: Dùng thư viện đồ thị như Plotly, Altair, hoặc Matplotlib/Seaborn
#     # Ví dụ: Tưởng tượng code trực quan hóa ở đây
#     st.text(f"Đang hiển thị biểu đồ cho: {', '.join(quoc_gia_da_chon)}")
#     st.text(f"Thang đo: {'Logarit' if su_dung_log_scale else 'Linear'}")
#
#     #
#     # Dòng code biểu đồ thực tế sẽ nằm ở đây (ví dụ dùng Altair):
#     # chart = alt.Chart(df_so_sanh).mark_line().encode(...)
#     # st.altair_chart(chart, use_container_width=True)