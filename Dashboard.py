import streamlit as st
from streamlit_autorefresh import st_autorefresh
# https://docs.streamlit.io/develop/api-reference 
# "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
from All import data_collector as data
from datetime import datetime

st.set_page_config(page_title="PV Dashboard", layout="wide")
st.title("PV-Dashboard")

left, middle, right = st.columns(3)
if left.button("Fems-Dashboard", width="stretch"):
    st.switch_page("pages/Fems.py")
if middle.button("Main-Dashboard", width="stretch"):
    st.switch_page("Dashboard.py")
if right.button("AP-Dashboard", width="stretch"):
    st.switch_page("pages/AP.py")


# Daten alle 5 Sekunden aktualisieren
st_autorefresh(interval=5 * 1000, key="datarefresh")
st.write(f"🔄 Letzte Aktualisierung: {datetime.now().strftime('%H:%M:%S')}")