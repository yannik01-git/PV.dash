import requests


# FEMS API URL Abfrage der Daten
try:
    response = requests.get('http://192.168.188.66:80', timeout=5) # Timeout hinzufügen
    # Erfolgreiche Anfrage wird hier behandelt

    user = 'Gast'
    password = 'user'

    session = requests.Session()
    session.auth = (user, password)

    # SOC abfragen
    url = 'http://Gast:user@192.168.188.66:80/rest/channel/_sum/EssSoc'
    charging_state = session.get(url)
    charging_state.raise_for_status()

    # Netzbezug abfragen
    url = 'http://Gast:user@192.168.188.66:80/rest/channel/_sum/GridActivePower'
    grid_power = session.get(url)
    grid_power.raise_for_status()

    # Batterieleistung abfragen
    url = 'http://Gast:user@192.168.188.66:80/rest/channel/_sum/EssActivePower'
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

except requests.exceptions.RequestException as e:
    print(f"Fehler bei der Anfrage: {e}")
    # Hier können Sie auch Fehler wie Timeout behandeln
# --------------------------------------------------------
# AP-Garage 
# --------------------------------------------------------
# PV-Leistung abfragen
try:
    response = requests.get('http://192.168.188.63:8050', timeout=5) # Timeout hinzufügen
    # Erfolgreiche Anfrage wird hier behandelt
    url = 'http://192.168.188.63:8050/get_output_data'
    garage_ap = session.get(url)
    garage_ap.raise_for_status()
except requests.exceptions.RequestException as e:
    print(f"Fehler bei der Anfrage: {e}")
    # Hier können Sie auch Fehler wie Timeout behandeln


