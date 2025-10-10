import streamlit as st
from streamlit_autorefresh import st_autorefresh
# https://docs.streamlit.io/develop/api-reference 
# "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
from All import data_collector as data
from All import data_saver_20_min as saver1
from All import data_saver_1_hour as saver2
from All import data_saver_day as saver3
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
st_autorefresh(interval=5 * 1000, key="dashrefresh")
st.write(f"🔄 Letzte Aktualisierung: {datetime.now().strftime('%H:%M:%S')}")

# Daten speichern
saver1.save_20min()
saver2.save_1hour()
saver3.save_day()

if data.fems_online:
    Fems = data.production_power.json().get('value', 0)
    Netz = data.grid_power.json().get('value', 0)
    Balkon = data.fems_balkon
    Garage = data.garage_produktion
    Spielvilla = data.spielvilla_produktion
    Battery = data.battery_power.json().get('value', 0)
    Ladung = data.charging_state.json().get('value', 0) 
    Haus = data.haus_verbrauch
else:
    Fems = 0
    Netz = 0
    Balkon = 0
    Garage = 0
    Spielvilla = 0
    Battery = 0
    Ladung = 0
    Haus = 0

left, middle, right = st.columns(3)
prod_matrix = pd.DataFrame({
    "Fems": [f"{Fems} W"],
    "Balkon": [f"{Balkon} W"],
    "Garage": [f"{Garage} W"],
    "Spielvilla": [f"{Spielvilla} W"]
},
index=["Produktion"],
)
middle.table(prod_matrix)

left, middle, right = st.columns(3)
if Netz > 0:
    #left.button("Netzeinspeisung",width="stretch")
    #left.button(f"{-Netz} W", width="stretch")
    left.metric("Netzbezug",f"{Netz} W")
elif Netz <= 0:
    #left.button("Netzbezug",width="stretch")
    #left.button(f"{Netz} W", width="stretch")
    left.metric("Netzeinspeisung",f"{-Netz} W")

#right.button("Verbrauch", width="stretch")
#right.button(f"{Haus} W", width="stretch")
right.metric("Verbrauch", f"{Haus} W")


left, middle, right = st.columns(3)
if Battery < 0:
    middle.button("Batteriebeladung", width="stretch")
    middle.button(f"{-Battery} W", width="stretch")
elif Battery > 0:
    middle.button("Batterieentladung", width="stretch")
    middle.button(f"{Battery} W", width="stretch")
elif Battery == 0:
    middle.button("Batterie neutral", width="stretch")
    middle.button(f"{Battery} W", width="stretch")
middle.button(f"{Ladung} %", width="stretch")