import streamlit as st
from streamlit import sidebar
from style import set_custom_css  # nếu tách file
# GỌI CSS TRƯỚC
set_custom_css()

st.set_page_config(page_title="COVID-19 Analysis System", layout="wide", page_icon="image/logo.jpg")

st.title("COVID-19 Dashboard 🦠")
st.write("Welcome to the COVID-19 analysis system!")

sidebar.title("COVID-19 Analysis System")
selected_tab = st.sidebar.radio("Select Tab", ["Home", "About"])