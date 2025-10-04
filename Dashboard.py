import streamlit as st
# https://docs.streamlit.io/develop/api-reference 
# "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
from All import data_fetch as data

st.title("PV-Dashboard")

left, right = st.columns(2)
if left.button("Fems-Dashboard", width="stretch"):
    st.switch_page("pages/Fems.py")
if right.button("AP-Dashboard", width="stretch"):
    st.switch_page("pages/AP.py")

st.metric(label="Fems Produktion", value=data.fems_values["fems1"]["production"])