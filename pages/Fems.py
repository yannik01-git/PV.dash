import streamlit as st
import All.data_fetch as data
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
import threading
import asyncio
from All import data_fetch as rechner
import http
import requests

st.set_page_config(page_title="FEMS Monitor", layout="wide")

st.title("🔋 FEMS Live-Daten")


left, middle, right = st.columns(3)
if left.button("Fems-Dashboard", width="stretch"):
    st.switch_page("pages/Fems.py")
if middle.button("Main-Dashboard", width="stretch"):
    st.switch_page("Dashboard.py")
if right.button("AP-Dashboard", width="stretch"):
    st.switch_page("pages/AP.py")

# --------------------------------------------------------
# Auto-Refresh alle 5 Sekunden
# --------------------------------------------------------
st_autorefresh(interval=5 * 1000, limit=None, key="auto")
st.write(f"🔄 Letzte Aktualisierung: {datetime.now().strftime('%H:%M:%S')}")


url = 'http://Gast:user@192.168.188.66:80/rest/channel/_sum/EssSoc'

user = 'Gast'
password = 'user'

session = requests.Session()
session.auth = (user, password)

charging_state = session.get(url)
charging_state.raise_for_status()

st.metric("Ladezustand", f"{charging_state.json().get('value', 0)} %")