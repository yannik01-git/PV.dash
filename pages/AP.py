import streamlit as st
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
from All import data_collector as data

st.set_page_config(page_title="AP Monitor", layout="wide")
st.title("🔌 AP-Dashboard")

# Navigation
left, middle, right = st.columns(3)
if left.button("Fems-Dashboard"):
    st.switch_page("pages/Fems.py")
if middle.button("Main-Dashboard"):
    st.switch_page("Dashboard.py")
if right.button("AP-Dashboard"):
    st.switch_page("pages/AP.py")

# Automatische Datenaktualisierung alle 5 Sekunden
st_autorefresh(interval=5 * 1000, key="auto_ap")
st.caption(f"🔄 Letzte Aktualisierung: {datetime.now().strftime('%H:%M:%S')}")

# --------------------------------------------------------
# Live-Daten abrufen
# --------------------------------------------------------
garage = data.fetch_garage_data()
spielvilla = data.fetch_spielvilla_data()

# --------------------------------------------------------
# Anzeige
# --------------------------------------------------------
left, middle, right = st.columns(3)
# ---------- GARAGE ----------

left.subheader("🚗 Garage")
if garage["online"]:
    left.metric("PV-Leistung 1", f"{garage['ap'].get('p1', 0)} W")
    left.metric("PV-Leistung 2", f"{garage['ap'].get('p2', 0)} W")
    left.metric("Leistungsgrenze", f"{garage['max_power'].get('maxPower', 0)} W")
else:
    left.metric("Status", "❓ Keine Verbindung")

# ---------- SPIELVILLA ----------
right.subheader("🏠 Spielvilla")
if spielvilla["online"]:
    right.metric("PV-Leistung 1", f"{spielvilla['ap'].get('p1', 0)} W")
    right.metric("PV-Leistung 2", f"{spielvilla['ap'].get('p2', 0)} W")
    right.metric("Leistungsgrenze", f"{spielvilla['max_power'].get('maxPower', 0)} W")
else:
    right.metric("Status", "❓ Keine Verbindung")
