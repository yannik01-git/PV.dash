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

fems = data.fetch_fems_data()
garage = data.fetch_garage_data()
spielvilla = data.fetch_spielvilla_data()
combined = data.fetch_combined_data()

left, middle, right = st.columns(3)
prod_matrix = pd.DataFrame({
    "Fems": [f"{fems['production_power']} W"],
    "Balkon": [f"{fems['balkon']} W"],
    "Garage": [f"{garage['ap']} W"],
    "Spielvilla": [f"{spielvilla['ap']} W"]
},
index=["Produktion"],
)
middle.table(prod_matrix)

left, middle, right = st.columns(3)
left.button("Netz",width="stretch")
left.button(f"{fems['grid_power']} W", width="stretch")

middle.badge("+", color = "green", width="stretch")

right.button("Verbrauch", width="stretch")
right.button(f"{combined['consumption_total']} W", width="stretch")

left, middle, right = st.columns(3)
middle.button("Batterie", width="stretch")
middle.button(f"{fems['charging_state']} W", width="stretch")