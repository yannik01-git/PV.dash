import streamlit as st
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
from All import data_collector as data
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
# Auto-Refresh alle 10 Sekunden
# --------------------------------------------------------
st_autorefresh(interval=10 * 1000, limit=None, key="femsrefresh")
st.write(f"🔄 Letzte Aktualisierung: {datetime.now().strftime('%H:%M:%S')}")

data.refreshState()

if data.fems_online:
    left, right = st.columns(2)
    # Erfolgreiche Anfrage wird hier behandelt
    # --------------------------------------------------------
    # FEMS Batterie anzeigen
    left.metric("Ladezustand", f"{data.charging_state.json().get('value', 0)} %")

    if data.battery_power.json().get('value', 0) >= 0:
        left.metric("Batterieentladung", f"{data.battery_power.json().get('value', 0)} W")
    elif data.battery_power.json().get('value', 0) < 0:
        left.metric("Batteriebeladung", f"{-data.battery_power.json().get('value', 0)} W")

    # --------------------------------------------------------
    # Fems Erzeugung
    left.metric("Erzeugung", f"{data.production_power.json().get('value', 0)} W")

    # --------------------------------------------------------
    # Fems Netzbezug/Netzeinspeisung anzeigen
    if data.grid_power.json().get('value', 0) >= 0:
        left.metric("Netzbezug", f"{data.grid_power.json().get('value', 0)} W")
    elif data.grid_power.json().get('value', 0) < 0:
        left.metric("Netzeinspesung", f"{-data.grid_power.json().get('value', 0)} W")

    # --------------------------------------------------------
    # FEMS Verbrauch anzeigen
    left.metric("Verbrauch", f"{data.consumption.json().get('value', 0)} W")

    # --------------------------------------------------------
    # Fems Zustand anzeigen
    if data.status.json().get('value') == 0:
        right.metric("FEMS Status", "✅ OK")
    elif data.status.json().get('value') ==1:
        right.metric("FEMS Status", "⚠️ Info")
    elif data.status.json().get('value') ==2:
        right.metric("FEMS Status", "❗ Warnung")
    elif data.status.json().get('value') ==3:
        right.metric("FEMS Status", "⛔ Fehler")
    else:
        right.metric("FEMS Status","❓ Unbekannt")

    # --------------------------------------------------------
    # Fems Grid Mode anzeigen
    if data.grid_mode.json().get('value') ==1:
        right.metric("FEMS Grid Mode","🔌 Netzbetrieb")
    elif data.grid_mode.json().get('value') ==2:
        right.metric("FEMS Grid Mode", "🔋 Inselbetrieb")
    else:
        right.metric("FEMS Grid Mode", "❓ Unbekannt")

else:
    # Hier können Sie auch Fehler wie Timeout behandeln
    st.metric("Status", "❓ Keine Verbindung")