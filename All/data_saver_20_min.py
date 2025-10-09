from All import data_collector as data
import os
from datetime import datetime, timedelta
import csv

ordner_pfad = "Speicherung"
os.makedirs(ordner_pfad, exist_ok=True)

save_intervall = timedelta(minutes=20)
last_save = None
heute = datetime.now().strftime("%Y_%m_%d")
dateiname = f"{heute}_20min.csv"
dateipfad = os.path.join(ordner_pfad, dateiname)

def save_data(erzeugung_fems, erzeugung_garage, erzeugung_spielvilla, verbrauch, netzeinspeisung, netzbezug):
    global last_save
    datum = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(dateipfad, mode='a', newline='', encoding='utf-8') as csv_datei:
        writer = csv.writer(csv_datei)
        writer.writerow([datum, erzeugung_fems, erzeugung_garage, erzeugung_spielvilla, verbrauch, netzeinspeisung, netzbezug])
    last_save = datetime.now()
    print(f"Daten gespeichert in {dateipfad}")

def save_old_data():
    if data.garage_online:
        erzeugung_garage = data.garage_ap.json().get('e1', 0) + data.garage_ap.json().get('e2', 0)
    else:
        erzeugung_garage = 0
    if data.spielvilla_online:
        erzeugung_spielvilla = data.spielvilla_ap.json().get('e1', 0) + data.spielvilla_ap.json().get('e2', 0)
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
        if not os.path.exists(dateipfad):
            with open(dateipfad, mode='w', newline='', encoding='utf-8') as csv_datei:
                writer = csv.writer(csv_datei)
                writer.writerow(["Datum", "Erzeugung Fems", "Erzeugung Garage", "Erzeugung Spielvilla", "Verbrauch", "Netzeinspeisung", "Netzbezug"])
            print(f"Neue CSV-Datei erstellt: {dateipfad}")
        
        erzeugung_fems, erzeugung_garage, erzeugung_spielvilla, verbrauch, netzeinspeisung, netzbezug = save_old_data()
        save_data(erzeugung_fems, erzeugung_garage, erzeugung_spielvilla, verbrauch, netzeinspeisung, netzbezug)

    elif last_save is None:
        last_save = jetzt
        save_old_data()
