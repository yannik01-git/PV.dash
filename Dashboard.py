import streamlit as st
from streamlit_autorefresh import st_autorefresh
# https://docs.streamlit.io/develop/api-reference 
# "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
from All import data_collector as data
from datetime import datetime
import pandas as pd

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

left, middle, right = st.columns(3)
prod_matrix = pd.DataFrame({
    "Fems": [f"{data.production_power.json().get('value', 0)} W"],
    "Balkon": [f"{data.fems_balkon} W"],
    "Garage": [f"{data.garage_produktion} W"],
    "Spielvilla": [f"{data.spielvilla_produktion} W"]
},
index=["Produktion"],
)
middle.table(prod_matrix)

left, middle, right = st.columns(3)
if data.grid_power.json().get('value', 0) < 0:
    left.button("Netzeinspeisung",width="stretch")
    left.button(f"{data.grid_power.json().get('value', 0)} W", width="stretch")
elif data.grid_power.json().get('value', 0) >= 0:
    left.button("Netzbezug",width="stretch")
    left.button(f"{data.grid_power.json().get('value', 0)} W", width="stretch")

right.button("Verbrauch", width="stretch")
right.button(f"{data.haus_verbrauch}" "W", width="stretch")

left, middle, right = st.columns(3)
if data.battery_power.json().get('value', 0) < 0:
    middle.button("Batterieentladung", width="stretch")
    middle.button(f"{-data.battery_power.json().get('value', 0)} W", width="stretch")
elif data.battery_power.json().get('value', 0) > 0:
    middle.button("Batteriebeladung", width="stretch")
    middle.button(f"{data.battery_power.json().get('value', 0)} W", width="stretch")
elif data.battery_power.json().get('value', 0) == 0:
    middle.button("Batterie neutral", width="stretch")
    middle.button(f"{data.battery_power.json().get('value', 0)} W", width="stretch")
middle.button(f"{data.charging_state.json().get('value', 0)} %", width="stretch")