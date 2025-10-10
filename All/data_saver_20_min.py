from All import data_collector as data
import os
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh
import csv

# Daten alle 10 Sekunden aktualisieren
st_autorefresh(interval=10 * 1000, key="save20refresh")
#st.write(f"🔄 Letzte Aktualisierung: {datetime.now().strftime('%H:%M:%S')}")

# Globale Variablen für die letzte Speicherung und Basisdaten
jetzt = datetime.now()
last_save = None
old_erzeugung_fems = 0
old_erzeugung_garage = 0 
old_erzeugung_spielvilla = 0
old_verbrauch = 0
old_netzeinspeisung = 0
old_netzbezug = 0

# Pfad zum Speicherordner
ordner_pfad = "Speicherung"

# Sicherstellen, dass der Ordner existiert
os.makedirs(ordner_pfad, exist_ok=True)

# Heutiges Datum im Format Jahr_Monat_Tag
heute = datetime.now().strftime("%Y_%m_%d")

# Dateiname
save_intervall = timedelta(minutes=3)  # Korrigiert auf 3 Minuten
dateiname = f"{heute}_20min.csv"
dateipfad = os.path.join(ordner_pfad, dateiname)

def save_data(erzeugung_fems, erzeugung_garage, erzeugung_spielvilla, verbrauch, netzeinspeisung, netzbezug):
    datum = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(dateipfad, mode='a', newline='', encoding='utf-8') as csv_datei:
        writer = csv.writer(csv_datei, delimiter=';')
        writer.writerow([datum, erzeugung_fems, erzeugung_garage, erzeugung_spielvilla, verbrauch, netzeinspeisung, netzbezug])
    print(f"Daten gespeichert in {dateipfad}")

def update_baseline_data():
    """Aktualisiert die Basisdaten für die nächste Differenzberechnung"""
    global old_erzeugung_fems, old_erzeugung_garage, old_erzeugung_spielvilla
    global old_verbrauch, old_netzeinspeisung, old_netzbezug
    
    if data.garage_online:
        old_erzeugung_garage = data.garage_data.get('e1', 0) + data.garage_data.get('e2', 0)
    else:
        old_erzeugung_garage = 0
        
    if data.spielvilla_online:
        old_erzeugung_spielvilla = data.spielvilla_data.get('e1', 0) + data.spielvilla_data.get('e2', 0)
    else:
        old_erzeugung_spielvilla = 0
        
    if data.fems_online:
        old_erzeugung_fems = data.full_production.json().get('value', 0)
        old_verbrauch = data.full_consumption.json().get('value', 0)
        old_netzeinspeisung = data.grid_sell.json().get('value', 0)
        old_netzbezug = data.grid_buy.json().get('value', 0)
    else:
        old_erzeugung_fems = old_verbrauch = old_netzeinspeisung = old_netzbezug = 0

    print("Basisdaten für nächste Berechnung aktualisiert")

def save_20min():
    global last_save
    jetzt = datetime.now()

    # Erste Initialisierung - nur Zeitstempel setzen, keine Daten speichern
    if last_save is None:
        last_save = jetzt
        update_baseline_data()  # Basisdaten für nächste Berechnung sammeln
        return
    
    # Intervall abgelaufen - Daten speichern
    if (jetzt - last_save) >= save_intervall:
        
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
        else:
            print(f"Datei existiert bereits: {dateipfad}")
        
        # Aktuelle Werte abrufen und Differenz zu den Basisdaten berechnen
        if data.garage_online:
            current_garage = data.garage_data.get('e1',0) + data.garage_data.get('e2',0)
            erzeugung_garage = current_garage - old_erzeugung_garage
        else:
            erzeugung_garage = 0

        
        if data.spielvilla_online:
            current_spielvilla = data.spielvilla_data.get('e1',0) + data.spielvilla_data.get('e2',0)
            erzeugung_spielvilla = current_spielvilla - old_erzeugung_spielvilla
        else:
            erzeugung_spielvilla = 0

        if data.fems_online:
            current_fems = data.full_production.json().get('value',0)
            current_verbrauch = data.full_consumption.json().get('value',0)
            current_netzeinspeisung = data.grid_sell.json().get('value',0)
            current_netzbezug = data.grid_buy.json().get('value',0)
            
            erzeugung_fems = current_fems - old_erzeugung_fems
            verbrauch = current_verbrauch - old_verbrauch
            netzeinspeisung = current_netzeinspeisung - old_netzeinspeisung
            netzbezug = current_netzbezug - old_netzbezug
        else:
            erzeugung_fems = verbrauch = netzeinspeisung = netzbezug = 0
            
        # Daten speichern
        save_data(erzeugung_fems, erzeugung_garage, erzeugung_spielvilla, verbrauch, netzeinspeisung, netzbezug)
        
        # Zeitstempel und Basisdaten für nächsten Durchlauf aktualisieren
        last_save = jetzt
        update_baseline_data()
