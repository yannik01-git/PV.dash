import streamlit as st
from streamlit_autorefresh import st_autorefresh


st.title("AP-Dashboard")

# Daten alle 5 Sekunden aktualisieren
st_autorefresh(interval=5 * 1000, key="datarefresh")

left, middle, right = st.columns(3)
if left.button("Fems-Dashboard", width="stretch"):
    st.switch_page("pages/Fems.py")
if middle.button("Main-Dashboard", width="stretch"):
    st.switch_page("Dashboard.py")
if right.button("AP-Dashboard", width="stretch"):
    st.switch_page("pages/AP.py")