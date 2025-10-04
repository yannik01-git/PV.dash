import streamlit as st

st.title("Fems-Dashboard")

left, right = st.columns(2)
if left.button("AP-Dashboard", width="stretch"):
    st.switch_page("pages/AP.py")
if right.button("Main-Dashboard", width="stretch"):
    st.switch_page("Dashboard.py")