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
# Auto-Refresh alle 5 Sekunden
# --------------------------------------------------------
st_autorefresh(interval=5 * 1000, limit=None, key="auto")
st.write(f"🔄 Letzte Aktualisierung: {datetime.now().strftime('%H:%M:%S')}")

try:
    response = requests.get('http://192.168.188.66:80', timeout=5) # Timeout hinzufügen
    # Erfolgreiche Anfrage wird hier behandelt
    # --------------------------------------------------------
    # FEMS Batterie anzeigen
    st.metric("Ladezustand", f"{data.charging_state.json().get('value', 0)} %")

    if data.battery_power.json().get('value', 0) <= 0:
        st.metric("Batteriebeladung", f"{data.battery_power.json().get('value', 0)} W")
    elif data.battery_power.json().get('value', 0) > 0:
        st.metric("Batterieentladung", f"{data.battery_power.json().get('value', 0)} W")

    # --------------------------------------------------------
    # Fems Netzbezug/Netzeinspeisung anzeigen
    if data.grid_power.json().get('value', 0) >= 0:
        st.metric("Netzeinspeisung", f"{data.grid_power.json().get('value', 0)} W")
    elif data.grid_power.json().get('value', 0) < 0:
        st.metric("Netzbezug", f"{-data.grid_power.json().get('value', 0)} W")

    # --------------------------------------------------------
    # FEMS Verbrauch anzeigen
    st.metric("Verbrauch", f"{data.consumption.json().get('value', 0)} W")

    # --------------------------------------------------------
    # Fems Zustand anzeigen
    if data.status.json().get('value') == 0:
        st.metric("FEMS Status", "✅ OK")
    elif data.status.json().get('value') ==1:
        st.metric("FEMS Status", "⚠️ Info")
    elif data.status.json().get('value') ==2:
        st.metric("FEMS Status", "❗ Warnung")
    elif data.status.json().get('value') ==3:
        st.metric("FEMS Status", "⛔ Fehler")
    else:
        st.metric("FEMS Status","❓ Unbekannt")

    # --------------------------------------------------------
    # Fems Grid Mode anzeigen
    if data.grid_mode.json().get('value') ==1:
        st.metric("FEMS Grid Mode","🔌 Netzbetrieb")
    elif data.grid_mode.json().get('value') ==2:
        st.metric("FEMS Grid Mode", "🔋 Inselbetrieb")
    else:
        st.metric("FEMS Grid Mode", "❓ Unbekannt")

except requests.exceptions.RequestException as e:
    print(f"Fehler bei der Anfrage: {e}")
    # Hier können Sie auch Fehler wie Timeout behandeln
    st.metric("Status", "❓ Keine Verbindung")