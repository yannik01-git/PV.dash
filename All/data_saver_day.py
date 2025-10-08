from All import data_collector as data
import os
from datetime import datetime, timedelta
import csv
from streamlit_autorefresh import st_autorefresh
import streamlit as st

st.title("📊 Automatische Datenspeicherung")

# Daten alle 5 Sekunden aktualisieren
st_autorefresh(interval=20 * 1000, key="datarefresh")

# Globale Variable für die letzte Speicherung
jetzt = datetime.now()
last_save = None

# Pfad zum Speicherordner
ordner_pfad = "Speicherung"

# Sicherstellen, dass der Ordner existiert
os.makedirs(ordner_pfad, exist_ok=True)

# Heutiges Datum im Format Jahr_Monat_Tag
heute = datetime.now().strftime("%Y_%m_%d")

# Dateiname
dateiname = f"{heute}_1day.csv"
dateipfad = os.path.join(ordner_pfad, dateiname)


# ---------------------------------------------------------
# Funktionen zum Speichern der Daten 

def save_data(erzeugung_fems, erzeugung_garage, erzeugung_spielvilla, verbrauch, netzeinspeisung, netzbezug):
    """
    Speichert eine neue Zeile mit Messwerten in die heutige CSV-Datei.
    Die aktuelle Uhrzeit (Datum+Zeit) wird automatisch in die erste Spalte geschrieben.
    """
    datum = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Neue Zeile hinzufügen
    with open(dateipfad, mode='a', newline='', encoding='utf-8') as csv_datei:
        writer = csv.writer(csv_datei)
        writer.writerow([
            datum,
            erzeugung_fems,
            erzeugung_garage,
            erzeugung_spielvilla,
            verbrauch,
            netzeinspeisung,
            netzbezug
        ])
    last_save = jetzt  # Zeitstempel aktualisieren
    return last_save
    print(f"Daten gespeichert in {dateipfad}")

def save_old_data():
    if data.garage_online:
        erzeugung_garage = data.garage_ap.json().get('e1',0)+data.garage_ap.json().get('e2',0)
    else:
        erzeugung_garage = 0
    if data.spielvilla_online:
        erzeugung_spielvilla = data.spielvilla_ap.json().get('e1',0) + data.spielvilla_ap.json().get('e2',0)
    else:
        erzeugung_spielvilla = 0
    if data.fems_online:
        erzeugung_fems = data.full_production.json().get('value',0)
        verbrauch = data.full_consumption.json().get('value',0)
        netzeinspeisung = data.grid_sell.json().get('value',0)
        netzbezug = data.grid_buy.json().get('value',0)
    else:
        erzeugung_fems = 0
        verbrauch = 0
        netzeinspeisung = 0
        netzbezug = 0

    # Werte zurückgeben
    return erzeugung_fems, erzeugung_garage, erzeugung_spielvilla, verbrauch, netzeinspeisung, netzbezug



# Zeitfunktion zum Speichern
if last_save is not None and datetime.now().strftime("%Y_%m_%d") >= heute:

    # Prüfen, ob die Datei existiert
    if not os.path.exists(dateipfad):
        # Datei erstellen (mit Kopfzeile als Beispiel)
        with open(dateipfad, mode='w', newline='', encoding='utf-8') as csv_datei:
            writer = csv.writer(csv_datei)
            writer.writerow([
                "Datum",
                "Erzeugung Fems",
                "Erzeugung Garage",
                "Erzeugung Spielvilla",
                "Verbrauch",
                "Netzeinspeisung",
                "Netzbezug"
            ])
        print(f"Neue CSV-Datei erstellt: {dateipfad}")
    elif last_save is None:
        last_save = jetzt
        save_old_data()
    else:
        print(f"Datei existiert bereits: {dateipfad}")
    erzeugung_fems, erzeugung_garage, erzeugung_spielvilla, verbrauch, netzeinspeisung, netzbezug = save_old_data()
    erzeugung_garage = data.garage_ap.json().get('e1',0)+data.garage_ap.json().get('e2',0) - erzeugung_garage
    erzeugung_spielvilla = data.spielvilla_ap.json().get('e1',0) + data.spielvilla_ap.json().get('e2',0) - erzeugung_spielvilla
    erzeugung_fems = data.full_production.json().get('value',0) - erzeugung_fems
    verbrauch = data.full_consumption.json().get('value',0) + erzeugung_garage + erzeugung_fems - verbrauch
    netzeinspeisung = data.grid_sell.json().get('value',0) - netzeinspeisung
    netzbezug = data.grid_buy.json().get('value',0) - netzbezug
    save_data(erzeugung_fems, erzeugung_garage, erzeugung_spielvilla, verbrauch, netzeinspeisung, netzbezug)
    save_old_data()