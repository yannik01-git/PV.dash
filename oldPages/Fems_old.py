import streamlit as st
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
from oldPages import data_collector_old as data
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

# --------------------------------------------------------
# Daten neu abrufen
# --------------------------------------------------------
fems = data.fetch_fems_data()

if fems["online"]:
    left, right = st.columns(2)
    left.metric("Ladezustand", f"{fems['charging_state']} %")

    power = fems["battery_power"]
    if power <= 0:
        left.metric("Batteriebeladung", f"{power} W")
    else:
        left.metric("Batterieentladung", f"{power} W")

    left.metric("Erzeugung", f"{fems['production_power']} W")
    left.metric("Balkon", f"{fems['balkon']} W")

    grid = fems["grid_power"]
    if grid <= 0:
        left.metric("Netzeinspeisung", f"{-grid} W")
    else:
        left.metric("Netzbezug", f"{grid} W")

    left.metric("Verbrauch", f"{fems['consumption']} W")

    # Status anzeigen
    status_map = {0: "✅ OK", 1: "⚠️ Info", 2: "❗ Warnung", 3: "⛔ Fehler"}
    right.metric("FEMS Status", status_map.get(fems["status"], "❓ Unbekannt"))

    # Grid Mode anzeigen
    mode_map = {1: "🔌 Netzbetrieb", 2: "🔋 Inselbetrieb"}
    right.metric("FEMS Grid Mode", mode_map.get(fems["grid_mode"], "❓ Unbekannt"))

else:
    st.metric("Status", "❓ Keine Verbindung")