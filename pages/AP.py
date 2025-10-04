import streamlit as st

st.title("AP-Dashboard")

left, right = st.columns(2)
if left.button("Fems-Dashboard", width="stretch"):
    st.switch_page("pages/Fems.py")
if right.button("Main-Dashboard", width="stretch"):
    st.switch_page("Dashboard.py")