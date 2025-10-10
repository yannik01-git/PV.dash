from All import data_collector as data
import os
from datetime import datetime
import csv
import streamlit as st
from streamlit_autorefresh import st_autorefresh

# Daten alle 10 Sekunden aktualisieren
st_autorefresh(interval=10 * 1000, key="savedayrefresh")

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
    global last_save
    datum = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Neue Zeile hinzufügen
    with open(dateipfad, mode='a', newline='', encoding='utf-8') as csv_datei:
        writer = csv.writer(csv_datei, delimiter=';')
        writer.writerow([
            datum,
            erzeugung_fems,
            erzeugung_garage,
            erzeugung_spielvilla,
            verbrauch,
            netzeinspeisung,
            netzbezug
        ])
    last_save = datetime.now().strftime("%Y-%m-%d")  # Zeitstempel aktualisieren
    print(f"Daten gespeichert in {dateipfad}")
    return last_save

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


def save_day():
    global last_save
    jetzt = datetime.now()
    current_day = datetime.now().strftime("%Y-%m-%d")
    
    # Erste Initialisierung
    if last_save is None:
        last_save = current_day
        return  # Beim ersten Aufruf nicht speichern, nur initialisieren
    
    # Zeitfunktion zum Speichern - speichern wenn neuer Tag beginnt
    if current_day > last_save:

        # Prüfen, ob die Datei existiert
        if not os.path.exists(dateipfad):
            # Datei erstellen (mit Kopfzeile als Beispiel)
            with open(dateipfad, mode='w', newline='', encoding='utf-8') as csv_datei:
                writer = csv.writer(csv_datei, delimiter=';')
                writer.writerow([
                    "Datum",
                    "Erzeugung Fems [Wh]",
                    "Erzeugung Garage [kWh]",
                    "Erzeugung Spielvilla [kWh]",
                    "Verbrauch [Wh]",
                    "Netzeinspeisung [Wh]",
                    "Netzbezug [Wh]"
                ])
            print(f"Neue CSV-Datei erstellt: {dateipfad}")
        
        # Alte Werte für Differenzberechnung holen
        erzeugung_fems, erzeugung_garage, erzeugung_spielvilla, verbrauch, netzeinspeisung, netzbezug = save_old_data()
        
        # Aktuelle Werte holen und Differenz berechnen
        if data.garage_online:
            erzeugung_garage = data.garage_ap.json().get('e1',0) + data.garage_ap.json().get('e2',0) - erzeugung_garage
        else:
            erzeugung_garage = 0
            
        if data.spielvilla_online:
            erzeugung_spielvilla = data.spielvilla_ap.json().get('e1',0) + data.spielvilla_ap.json().get('e2',0) - erzeugung_spielvilla
        else:
            erzeugung_spielvilla = 0
            
        if data.fems_online:
            erzeugung_fems = data.full_production.json().get('value',0) - erzeugung_fems
            verbrauch = data.full_consumption.json().get('value',0) - verbrauch
            netzeinspeisung = data.grid_sell.json().get('value',0) - netzeinspeisung
            netzbezug = data.grid_buy.json().get('value',0) - netzbezug
        else:
            erzeugung_fems = 0
            verbrauch = 0
            netzeinspeisung = 0
            netzbezug = 0
            
        # Daten speichern
        save_data(erzeugung_fems, erzeugung_garage, erzeugung_spielvilla, verbrauch, netzeinspeisung, netzbezug)