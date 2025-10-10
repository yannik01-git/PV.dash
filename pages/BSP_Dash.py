import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="PV Dashboard BSP", layout="wide")
st.title("PV-Dashboard-BSP")

left, middle, right = st.columns(3)
if left.button("Fems-Dashboard", width="stretch"):
    st.switch_page("pages/Fems.py")
if middle.button("Main-Dashboard", width="stretch"):
    st.switch_page("Dashboard.py")
if right.button("AP-Dashboard", width="stretch"):
    st.switch_page("pages/AP.py")

# Daten alle 10 Sekunden aktualisieren
st_autorefresh(interval=10 * 1000, key="bsprefresh")
st.write(f"🔄 Letzte Aktualisierung: {datetime.now().strftime('%H:%M:%S')}")

left, middle, right = st.columns(3)
prod_matrix = pd.DataFrame({
    "Fems": ["300  W"],
    "Balkon": ["10 W"],
    "Garage": ["20 W"],
    "Spielvilla": ["50 W"]
},
index=["Produktion"],
)
middle.table(prod_matrix)

left, middle, right = st.columns(3)
left.button("Netz",width="stretch")
left.button("100 W", width="stretch")

with middle:
    st.markdown(f"<h1 style='text-align:center;font-size: 100px; color:green;'>{'\u002B'}</h1>", unsafe_allow_html=True)

right.button("Verbrauch", width="stretch")
right.button("200 W", width="stretch")

left, middle, right = st.columns(3)
middle.button("Batterie", width="stretch")
middle.button("50 W", width="stretch")