import streamlit as st
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
from All import data_collector as data

st.set_page_config(page_title="Settings", layout="wide")
st.title("⚙️ Einstellungen")

# Navigation
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

regelung = st.checkbox("Regelung aktiv", value = True)

