import streamlit as st
from streamlit_autorefresh import st_autorefresh
from All import data_collector as data
import requests
from datetime import datetime

st.set_page_config(page_title="AP Monitor", layout="wide")
st.title("AP-Dashboard")

left, middle, right = st.columns(3)
if left.button("Fems-Dashboard", width="stretch"):
    st.switch_page("pages/Fems.py")
if middle.button("Main-Dashboard", width="stretch"):
    st.switch_page("Dashboard.py")
if right.button("AP-Dashboard", width="stretch"):
    st.switch_page("pages/AP.py")

# Daten alle 5 Sekunden aktualisieren
st_autorefresh(interval=5 * 1000, key="aprefresh")
st.write(f"🔄 Letzte Aktualisierung: {datetime.now().strftime('%H:%M:%S')}")

# --------------------------------------------------------
# AP-Garage anzeigen
left, middle, right = st.columns(3)
left.title("Garage")
if data.garage_online:
    # Erfolgreiche Anfrage wird hier behandelt
    left.metric("PV-Leistung-1", f"{data.garage_data.get('p1', 0.0)} W")
    left.metric("PV-Leistung-2", f"{data.garage_data.get('p2', 0.0)} W")
    left.metric("Garage-Leistungsgrenze", f"{data.garage_limit.get('maxPower', 0)} W")
else:
    # Hier können Sie auch Fehler wie Timeout behandeln
    left.metric("Status", "❓ Keine Verbindung")



# --------------------------------------------------------
# AP-Spielvilla anzeigen
right.title("Spielvilla")
if data.spielvilla_online:
    # Erfolgreiche Anfrage wird hier behandelt
    right.metric("PV-Leistung-1", f"{data.spielvilla_data.json().get('p1', 0)} W")
    right.metric("PV-Leistung-2", f"{data.spielvilla_data.json().get('p2', 0)} W")
    right.metric("Spielvilla-Leistungsgrenze", f"{data.spielvilla_limit.json().get('maxPower', 0)} W")
else:
    # Hier können Sie auch Fehler wie Timeout behandeln
    right.metric("Status", "❓ Keine Verbindung")


# -------------------------------------------------------
# Gesamterzeugung anzeigen
left, middle, right = st.columns(3)
middle.metric("Gersamterzeugung AP", f"{data.ap_produktion} W")