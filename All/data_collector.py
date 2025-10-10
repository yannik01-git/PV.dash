import requests
from streamlit_autorefresh import st_autorefresh
import streamlit as st

# Daten alle 10 Sekunden aktualisieren
st_autorefresh(interval=10 * 1000, key="datarefresh")

# Globale Variablen für die Daten
fems_online = False
garage_online = False  
spielvilla_online = False
regelung_aktiv = False  # Wird von Settings.py gesetzt
charging_state = None
production_power = None
grid_power = None
battery_power = None
consumption = None
status = None
grid_mode = None
grid_buy = None
grid_sell = None
full_production = None
full_consumption = None
garage_ap = None
set_power_garage = None
get_power_garage = None
garage_data = {}
garage_limit = {}
spielvilla_ap = None
set_power_spielvilla = None
get_power_spielvilla = None
spielvilla_data = {}
spielvilla_limit = {}
garage_produktion = 0
spielvilla_produktion = 0
fems_balkon = 0
ap_produktion = 0
haus_verbrauch = 0
pv_produktion = 0

# FEMS API URL Abfrage der Daten
user = 'Gast'
password = 'user'

def setRegelung(status):
    """Setzt den Status der AP-Regelung"""
    global regelung_aktiv
    regelung_aktiv = status

def refreshState():
    """Aktualisiert alle Daten von den APIs bei jedem Aufruf"""
    global fems_online, garage_online, spielvilla_online
    global charging_state, production_power, grid_power, battery_power, consumption, status, grid_mode
    global grid_buy, grid_sell, full_production, full_consumption
    global garage_ap, set_power_garage, get_power_garage, garage_data, garage_limit
    global spielvilla_ap, set_power_spielvilla, get_power_spielvilla, spielvilla_data, spielvilla_limit
    global garage_produktion, spielvilla_produktion, fems_balkon, ap_produktion, haus_verbrauch, pv_produktion
    
    session = requests.Session()
    session.auth = (user, password)

    
    # --------------------------------------------------------
    # FEMS API Abfrage
    # --------------------------------------------------------
    try:
        response = requests.get('http://192.168.188.66:80', timeout=5) # Timeout hinzufügen
        # Erfolgreiche Anfrage wird hier behandelt

        fems_online = True

        # SOC abfragen
        url = 'http://Gast:user@192.168.188.66:80/rest/channel/_sum/EssSoc'
        charging_state = session.get(url)
        charging_state.raise_for_status()

        # Produktion abfragen
        url = 'http://Gast:user@192.168.188.66:80/rest/channel/_sum/ProductionActivePower'
        production_power = session.get(url)
        production_power.raise_for_status()

        # Netzbezug abfragen
        url = 'http://Gast:user@192.168.188.66:80/rest/channel/_sum/GridActivePower'
        grid_power = session.get(url)
        grid_power.raise_for_status()

        # Batterieleistung abfragen
        url = 'http://Gast:user@192.168.188.66:80/rest/channel/_sum/EssDischargePower'
        battery_power = session.get(url)
        battery_power.raise_for_status()

        # Verbrauch abfragen
        url = 'http://Gast:user@192.168.188.66:80/rest/channel/_sum/ConsumptionActivePower'
        consumption = session.get(url)
        consumption.raise_for_status()

        # FEMS Status abfragen
        url = 'http://Gast:user@192.168.188.66:80/rest/channel/_sum/State'
        status = session.get(url)
        status.raise_for_status()

        # FEMS Grid Mode abfragen
        url = 'http://Gast:user@192.168.188.66:80/rest/channel/_sum/GridMode'
        grid_mode = session.get(url)
        grid_mode.raise_for_status()

        # Fems Daten aus der Historie
        # Netzbezug
        url = 'http://Gast:user@192.168.188.66:80/rest/channel/_sum/GridBuyActiveEnergy'
        grid_buy = session.get(url)
        grid_buy.raise_for_status()

        # Netzeinspesung
        url = 'http://Gast:user@192.168.188.66:80/rest/channel/_sum/GridSellActiveEnergy'
        grid_sell = session.get(url)
        grid_sell.raise_for_status()

        # Produktion
        url = 'http://Gast:user@192.168.188.66:80/rest/channel/_sum/ProductionActiveEnergy'
        full_production = session.get(url)
        full_production.raise_for_status()

        # Verbrauch
        url = 'http://Gast:user@192.168.188.66:80/rest/channel/_sum/ConsumptionActiveEnergy'
        full_consumption = session.get(url)
        full_consumption.raise_for_status()

    except requests.exceptions.RequestException as e:
        fems_online = False
        print(f"Fehler bei der FEMS-Anfrage: {e}")
        # Variablen auf None setzen, wenn offline
        charging_state = None
        production_power = None
        grid_power = None
        battery_power = None
        consumption = None
        status = None
        grid_mode = None
        grid_buy = None
        grid_sell = None
        full_production = None
        full_consumption = None

    
    # --------------------------------------------------------
    # AP-Garage 
    # --------------------------------------------------------
    # PV-Leistung abfragen
    try:
        response = requests.get('http://192.168.188.63:8050', timeout=5) # Timeout hinzufügen
        # Erfolgreiche Anfrage wird hier behandelt
        garage_online = True
        # Leistungsdaten abfragen
        url = 'http://192.168.188.63:8050/getOutputData'
        garage_ap = session.get(url)
        garage_ap.raise_for_status()

        # Leistungsgrenze setzen (wird nur bei Bedarf in der Regelung aufgerufen)
        # url = f'http://192.168.188.63:8050/setMaxPower?p={power_value}'
        # Diese URL wird nur in der Regelung verwendet

        #Leistungsgrenze abfragen
        url = 'http://192.168.188.63:8050/getMaxPower'
        get_power_garage = session.get(url)
        get_power_garage.raise_for_status()

        garage_data = garage_ap.json().get("data", {})  # Unterobjekt "data"
        garage_limit = get_power_garage.json().get("data", {})

        # Daten aus der Garagen Historie
        # über e1 & e2 von getOutputData

    except requests.exceptions.RequestException as e:
        garage_online = False
        print(f"Fehler bei der Garage-Anfrage: {e}")
        # Variablen auf None/leeres Dict setzen, wenn offline
        garage_ap = None
        set_power_garage = None
        get_power_garage = None
        garage_data = {}
        garage_limit = {}

    
    # --------------------------------------------------------
    # AP-Spielvilla 
    # --------------------------------------------------------
    # PV-Leistung abfragen
    try:
        response = requests.get('http://192.168.188.122:8050', timeout=5) # Timeout hinzufügen
        # Erfolgreiche Anfrage wird hier behandelt
        spielvilla_online = True
        # Leistungsdaten abfragen
        url = 'http://192.168.188.122:8050/getOutputData'
        spielvilla_ap = session.get(url)
        spielvilla_ap.raise_for_status()

        # Leistungsgrenze setzen (wird nur bei Bedarf in der Regelung aufgerufen)
        # url = f'http://192.168.188.122:8050/setMaxPower?p={power_value}'
        # Diese URL wird nur in der Regelung verwendet

        #Leistungsgrenze abfragen
        url = 'http://192.168.188.122:8050/getMaxPower'
        get_power_spielvilla = session.get(url)
        get_power_spielvilla.raise_for_status()

        spielvilla_data = spielvilla_ap.json().get("data",{})
        spielvilla_limit = get_power_spielvilla.json().get("data",{})

        # Daten aus der Spielvilla Historie
        # über e1 & e2 von getOutputData

    except requests.exceptions.RequestException as e:
        spielvilla_online = False
        print(f"Fehler bei der Spielvilla-Anfrage: {e}")
        # Variablen auf None/leeres Dict setzen, wenn offline  
        spielvilla_ap = None
        set_power_spielvilla = None
        get_power_spielvilla = None
        spielvilla_data = {}
        spielvilla_limit = {}

    
    # --------------------------------------------------------
    # Gesamtdaten rechnen
    # --------------------------------------------------------
    if spielvilla_online and garage_online:
        garage_produktion = garage_data.get('p1', 0) + garage_data.get('p2', 0)
        spielvilla_produktion = spielvilla_data.get('p1', 0) + spielvilla_data.get('p2', 0)
        fems_balkon = 0
    elif spielvilla_online and (not garage_online):
        garage_produktion = 0
        spielvilla_produktion = spielvilla_data.get('p1', 0) + spielvilla_data.get('p2', 0)
        fems_balkon = 0
    elif garage_online and (not spielvilla_online):
        garage_produktion = garage_data.get('p1', 0) + garage_data.get('p2', 0)
        spielvilla_produktion = 0
        fems_balkon = 0
    else:
        garage_produktion = 0
        spielvilla_produktion = 0
        fems_balkon = 0

    ap_produktion = garage_produktion + spielvilla_produktion

    if fems_online  and consumption.json().get('value',0) >= 0:
        haus_verbrauch = consumption.json().get('value', 0) + abs(ap_produktion)
        pv_produktion = ap_produktion + production_power.json().get('value', 0)
        fems_balkon = 0

    elif not garage_online and not spielvilla_online and fems_online and consumption.json().get('value',0) < 0:
        haus_verbrauch = 0
        fems_balkon = abs(consumption.json().get('value', 0))
    elif fems_online and consumption.json().get('value',0) < 0 and (garage_online or spielvilla_online) and (not garage_online and not spielvilla_online):
        fems_balkon = abs(consumption.json().get('value', 0))- ap_produktion
        haus_verbrauch = consumption.json().get('value', 0) + abs(ap_produktion)
    elif garage_online and spielvilla_online and fems_online:
        fems_balkon = 0
        haus_verbrauch = consumption.json().get('value', 0) + abs(ap_produktion)
    else:
        haus_verbrauch = 0
        pv_produktion = ap_produktion
        fems_balkon = 0

    if fems_online and haus_verbrauch < 0:
        fems_balkon = abs(consumption.json().get('value', 0))+ fems_balkon
        haus_verbrauch = 0


    
    # ---------------------------------------------------------
    # AP-Regelung erstellen
    # --------------------------------------------------------
    min_power_ap = 30
    max_power_ap = 800

    # AP-Regelung nach unten 
    # Beide Module online
    # AP-Regelung (Status wird von Settings.py gesetzt)
    if spielvilla_online and garage_online:
        if regelung_aktiv:
            if garage_limit.get('maxPower',0) == garage_limit.get('maxPower',0) == max_power_ap:
                max_power_ap = max_power_ap
            elif ap_produktion > 800:
                diff_produktion = ap_produktion - max_power_ap
                if garage_produktion >= spielvilla_produktion and garage_produktion != min_power_ap:
                    new_power = int(f"{garage_limit.get('maxPower', 0) - diff_produktion}")
                    setGaragePower(new_power)
                elif garage_produktion >= spielvilla_produktion and garage_produktion == min_power_ap:
                    new_power = int(f"{spielvilla_limit.get('maxPower', 0) - diff_produktion}")
                    setSpielvillaPower(new_power)
                elif garage_produktion < spielvilla_produktion and spielvilla_produktion != min_power_ap:
                    new_power = int(f"{spielvilla_limit.get('maxPower', 0) - diff_produktion}")
                    setSpielvillaPower(new_power)
                elif garage_produktion < spielvilla_produktion and spielvilla_produktion == min_power_ap:
                    new_power = int(f"{garage_limit.get('maxPower', 0) - diff_produktion}")
                    setGaragePower(new_power)

            # AP-Regelung nach oben
            # Beide Module online
            elif ap_produktion < 750:
                diff_produktion = max_power_ap - ap_produktion
                if garage_produktion <= spielvilla_produktion and garage_produktion != max_power_ap:
                    new_power = int(f"{garage_limit.get('maxPower', 0) + diff_produktion}")
                    setGaragePower(new_power)
                elif garage_produktion <= spielvilla_produktion and garage_produktion == max_power_ap:
                    new_power = int(f"{spielvilla_limit.get('maxPower', 0) + diff_produktion}")
                    setSpielvillaPower(new_power)
                elif garage_produktion > spielvilla_produktion and spielvilla_produktion != max_power_ap:
                    new_power = int(f"{spielvilla_limit.get('maxPower', 0) + diff_produktion}")
                    setSpielvillaPower(new_power)
                elif garage_produktion > spielvilla_produktion and spielvilla_produktion == max_power_ap:
                    new_power = int(f"{garage_limit.get('maxPower', 0) + diff_produktion}")
                    setGaragePower(new_power)

def setGaragePower(power_value):
    """Setzt die maximale Leistung für die Garage-AP"""
    try:
        session = requests.Session()
        session.auth = (user, password)
        url = f'http://192.168.188.63:8050/setMaxPower?p={power_value}'
        response = session.get(url)
        response.raise_for_status()
        print(f"Garage-Power auf {power_value}W gesetzt")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Fehler beim Setzen der Garage-Power: {e}")
        return False

def setSpielvillaPower(power_value):
    """Setzt die maximale Leistung für die Spielvilla-AP"""
    try:
        session = requests.Session()
        session.auth = (user, password)
        url = f'http://192.168.188.122:8050/setMaxPower?p={power_value}'
        response = session.get(url)
        response.raise_for_status()
        print(f"Spielvilla-Power auf {power_value}W gesetzt")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Fehler beim Setzen der Spielvilla-Power: {e}")
        return False

# Initialer Aufruf beim Import
refreshState()
