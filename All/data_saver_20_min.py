from All import data_collector as data
import os
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh
import csv

# Daten alle 20 Sekunden aktualisieren
st_autorefresh(interval=20 * 1000, key="save20refresh")
#st.write(f"🔄 Letzte Aktualisierung: {datetime.now().strftime('%H:%M:%S')}")

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
save_intervall = timedelta(minutes=3)
dateiname = f"{heute}_20min.csv"
dateipfad = os.path.join(ordner_pfad, dateiname)

def save_data(erzeugung_fems, erzeugung_garage, erzeugung_spielvilla, verbrauch, netzeinspeisung, netzbezug):
    global last_save
    datum = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(dateipfad, mode='a', newline='', encoding='utf-8') as csv_datei:
        writer = csv.writer(csv_datei, delimiter=';')
        writer.writerow([datum, erzeugung_fems, erzeugung_garage, erzeugung_spielvilla, verbrauch, netzeinspeisung, netzbezug])
    last_save = datetime.now()
    print(f"Daten gespeichert in {dateipfad}")

def save_old_data():
    if data.garage_online:
        erzeugung_garage = data.garage_data.get('e1', 0) + data.garage_data.get('e2', 0)
    else:
        erzeugung_garage = 0
    if data.spielvilla_online:
        erzeugung_spielvilla = data.spielvilla_data.get('e1', 0) + data.spielvilla_data.get('e2', 0)
    else:
        erzeugung_spielvilla = 0
    if data.fems_online:
        erzeugung_fems = data.full_production.json().get('value', 0)
        verbrauch = data.full_consumption.json().get('value', 0)
        netzeinspeisung = data.grid_sell.json().get('value', 0)
        netzbezug = data.grid_buy.json().get('value', 0)
    else:
        erzeugung_fems = verbrauch = netzeinspeisung = netzbezug = 0

    return erzeugung_fems, erzeugung_garage, erzeugung_spielvilla, verbrauch, netzeinspeisung, netzbezug

def save_20min():
    global last_save
    jetzt = datetime.now()

    if last_save is not None and (jetzt - last_save) >= save_intervall:
        
        # Prüfen, ob die Datei existiert
        if not os.path.exists(dateipfad):
            # Datei erstellen (mit Kopfzeile als Beispiel)
            with open(dateipfad, mode='w', newline='', encoding='utf-8') as csv_datei:
                writer = csv.writer(csv_datei, delimiter=';')
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
        else:
            print(f"Datei existiert bereits: {dateipfad}")
        
        erzeugung_fems, erzeugung_garage, erzeugung_spielvilla, verbrauch, netzeinspeisung, netzbezug = save_old_data()

        if erzeugung_garage != 0 and data.garage_online:
            erzeugung_garage = data.garage_data.get('e1',0)+data.garage_data.get('e2',0) - erzeugung_garage
        else:
            erzeugung_garage = 0
        
        if erzeugung_spielvilla != 0 and data.spielvilla_online:
            erzeugung_spielvilla = data.spielvilla_data.get('e1',0) + data.spielvilla_data.get('e2',0) - erzeugung_spielvilla
        else:
            erzeugung_spielvilla = 0

        if erzeugung_fems != 0 and data.fems_online:
            erzeugung_fems = data.full_production.json().get('value',0) - erzeugung_fems
        else:
            erzeugung_fems = 0

        if verbrauch != 0 and data.fems_online:
            verbrauch = data.full_consumption.json().get('value',0) + erzeugung_garage + erzeugung_fems - verbrauch
        else:
            verbrauch = 0
        
        if netzeinspeisung != 0 and data.fems_online:
            netzeinspeisung = data.grid_sell.json().get('value',0) - netzeinspeisung
        else:
            netzeinspeisung = 0

        if netzbezug != 0 and data.fems_online:
            netzbezug = data.grid_buy.json().get('value',0) - netzbezug
        else:
            netzbezug = 0
        save_data(erzeugung_fems, erzeugung_garage, erzeugung_spielvilla, verbrauch, netzeinspeisung, netzbezug)
        save_old_data()
    elif last_save is None:
        last_save = jetzt
        save_old_data()
