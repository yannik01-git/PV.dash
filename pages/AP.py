import streamlit as st
from streamlit_autorefresh import st_autorefresh
from All import data_collector as data
import requests


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


# --------------------------------------------------------
# AP-Garage anzeigen
try:
    response = requests.get('http://192.168.188.63:8050', timeout=5) # Timeout hinzufügen
    # Erfolgreiche Anfrage wird hier behandelt
    left.metric("PV-Leistung", f"{data.garage_ap.json().get('p1', 0)} W")
except requests.exceptions.RequestException as e:
    print(f"Fehler bei der Anfrage: {e}")
    # Hier können Sie auch Fehler wie Timeout behandeln
    st.button("Garage", width="stretch")
    st.metric("Status", "❓ Keine Verbindung")
