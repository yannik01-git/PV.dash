import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="Energiefluss", layout="centered")

st.markdown("<h2 style='text-align:center;'>Energiefluss</h2>", unsafe_allow_html=True)

# Beispielwerte (können später dynamisch kommen)
solar_kw = 0.0
grid_kw = 0.0
battery_kw = 0.7
load_kw = 0.7

# Farben
COLOR_SOLAR = "#00BFFF"
COLOR_GRID = "#FFFFFF"
COLOR_BATTERY = "#00FF7F"
COLOR_LOAD = "#FFD700"
BG_COLOR = "#1E2433"

fig = go.Figure()

# Donut-Ring (Kreis)
fig.add_trace(go.Pie(
    values=[25, 25, 25, 25],
    hole=0.7,
    marker_colors=[COLOR_SOLAR, COLOR_GRID, COLOR_BATTERY, COLOR_LOAD],
    textinfo='none',
    rotation=90,
    showlegend=False
))

# 🔹 Symbole + Werte (innen zentriert)
fig.add_annotation(x=0, y=0.45, text=f"☀️<br>{solar_kw:.1f} kW", showarrow=False,
                   font=dict(size=16, color="white"), align="center")
fig.add_annotation(x=-0.45, y=0, text=f"⚡<br>{grid_kw:.1f} kW", showarrow=False,
                   font=dict(size=16, color="white"), align="center")
fig.add_annotation(x=0, y=-0.45, text=f"🔋<br>{battery_kw:.1f} kW", showarrow=False,
                   font=dict(size=16, color="white"), align="center")
fig.add_annotation(x=0.45, y=0, text=f"💡<br>{load_kw:.1f} kW", showarrow=False,
                   font=dict(size=16, color="white"), align="center")

# Layout-Anpassung
fig.update_layout(
    margin=dict(t=30, b=30, l=30, r=30),
    paper_bgcolor=BG_COLOR,
    plot_bgcolor=BG_COLOR,
    height=500,
)

st.plotly_chart(fig, use_container_width=True)
