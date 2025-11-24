from style import set_custom_css  # nếu tách file
import streamlit as st
import sys
import os

set_custom_css()
# Thêm backend vào sys.path để import được module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend')))

# Import class từ backend
from covid_app.services.visualizationController import CovidVisualizerOO

st.title("COVID-19 Visualization")

# Đường dẫn tới file Parquet
covid_data_path = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "..", "backend", "covid_app", "data", "cleaned_covid_data.parquet"
))

# Khởi tạo visualizer
visualizer = CovidVisualizerOO(covid_data_path)

# Chọn quốc gia
available_countries = visualizer.get_available_countries()
country = st.selectbox("Select country", available_countries)

# Vẽ biểu đồ số ca
fig_cases = visualizer.plot_cases(country)
st.pyplot(fig_cases)

# Vẽ biểu đồ tử vong
fig_deaths = visualizer.plot_deaths(country)
st.pyplot(fig_deaths)





