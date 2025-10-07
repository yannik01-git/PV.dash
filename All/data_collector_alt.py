import requests


# FEMS API URL Abfrage der Daten

user = 'Gast'
password = 'user'

session = requests.Session()
session.auth = (user, password)
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
    fems_online = False
    print(f"Fehler bei der Anfrage: {e}")
    # Hier können Sie auch Fehler wie Timeout behandeln

# --------------------------------------------------------
# AP-Garage 
# --------------------------------------------------------
# PV-Leistung abfragen
try:
    response = requests.get('http://192.168.188.63:8050', timeout=5) # Timeout hinzufügen
    # Erfolgreiche Anfrage wird hier behandelt
    garage_online = True
    # Leistungsdaten abfragen
    url = 'http://192.168.188.63:8050/get_output_data'
    garage_ap = session.get(url)
    garage_ap.raise_for_status()

    # Leistungsgrenze setzen
    url = 'http://192.168.188.63:8050/setMaxPower?p=600'
    set_power_garage = session.get(url)
    set_power_garage.raise_for_status()

    #Leistungsgrenze abfragen
    url = 'http://192.168.188.63:8050/getMaxPower'
    get_power_garage = session.get(url)
    get_power_garage.raise_for_status()

except requests.exceptions.RequestException as e:
    garage_online = False
    print(f"Fehler bei der Anfrage: {e}")
    # Hier können Sie auch Fehler wie Timeout behandeln


# --------------------------------------------------------
# AP-Spielvilla 
# --------------------------------------------------------
# PV-Leistung abfragen
try:
    response = requests.get('http://192.168.188.122:8050', timeout=5) # Timeout hinzufügen
    # Erfolgreiche Anfrage wird hier behandelt
    garage_online = True
    # Leistungsdaten abfragen
    url = 'http://192.168.188.122:8050/get_output_data'
    spielvilla_ap = session.get(url)
    spielvilla_ap.raise_for_status()

    # Leistungsgrenze setzen
    url = 'http://192.168.188.122:8050/setMaxPower'
    set_power_spielvilla = session.get(url)
    set_power_spielvilla.raise_for_status()

    #Leistungsgrenze abfragen
    url = 'http://192.168.188.122:8050/getMaxPower'
    get_power_spielvilla = session.get(url)
    get_power_spielvilla.raise_for_status()

except requests.exceptions.RequestException as e:
    spielvilla_online = False
    print(f"Fehler bei der Anfrage: {e}")
    # Hier können Sie auch Fehler wie Timeout behandeln


# --------------------------------------------------------
# Gesamtdaten rechnen
# --------------------------------------------------------
if spielvilla_online and garage_online:
    garage_produktion = garage_ap.json().get('p1', 0) + garage_ap.json().get('p2', 0)
    spielvilla_produktion = spielvilla_ap.json().get('p1', 0) + spielvilla_ap.json().get('p2', 0)
    fems_balkon = 0
elif spielvilla_online and not garage_online:
    garage_produktion = 0
    spielvilla_produktion = spielvilla_ap.json().get('p1', 0) + spielvilla_ap.json().get('p2', 0)
    fems_balkon = 0
elif not spielvilla_online and garage_online:
    garage_produktion = garage_ap.json().get('p1', 0) + garage_ap.json().get('p2', 0)
    spielvilla_produktion = 0
    fems_balkon = 0
else:
    garage_produktion = 0
    spielvilla_produktion = 0

ap_produktion = garage_produktion + spielvilla_produktion
if  fems_online:
    haus_verbrauch = consumption.json().get('value', 0) - ap_produktion
    pv_produktion = ap_produktion + production_power.json().get('value', 0)
    if  haus_verbrauch < 0 and fems_online:
        haus_verbrauch = 0
        fems_balkon = abs(consumption.json().get('value', 0))
else:
    haus_verbrauch = 0
    pv_produktion = ap_produktion
    fems_balkon = 0



# ---------------------------------------------------------
# AP-Regelung erstellen
# --------------------------------------------------------

min_power_ap = 30
max_power_ap = 800

# AP-Regelung nach unten 
# Beide Module online
if spielvilla_online and garage_online:
    if  ap_produktion > 800:
        diff_produktion = ap_produktion - max_power_ap
        if garage_produktion >= spielvilla_produktion and garage_produktion != min_power_ap:
            set_power_garage = get_power_garage.json().get('maxPower', 0) - diff_produktion
            if set_power_garage < min_power_ap:
                set_power_garage = min_power_ap
        elif garage_produktion >= spielvilla_produktion and garage_produktion == min_power_ap:
            set_power_spielvilla = get_power_spielvilla.json().get('maxPower', 0) - diff_produktion

        elif garage_produktion < spielvilla_produktion and spielvilla_produktion != min_power_ap:
            set_power_spielvilla = get_power_spielvilla.json().get('maxPower', 0) - diff_produktion
            if set_power_spielvilla < min_power_ap:
                set_power_spielvilla = min_power_ap
        elif garage_produktion < spielvilla_produktion and spielvilla_produktion == min_power_ap:
            set_power_spielvilla = get_power_spielvilla.json().get('maxPower', 0) - diff_produktion

    # AP-Regelung nach oben
    # Beide Module online
    elif ap_produktion < 750:
        diff_produktion =  max_power_ap - ap_produktion
        if garage_produktion <= spielvilla_produktion and garage_produktion != max_power_ap:
            set_power_garage = get_power_garage.json().get('maxPower', 0) + diff_produktion
            if set_power_garage > max_power_ap:
                set_power_garage = max_power_ap
        elif garage_produktion <= spielvilla_produktion and garage_produktion == max_power_ap:
            set_power_spielvilla = get_power_spielvilla.json().get('maxPower', 0) + diff_produktion

        elif garage_produktion > spielvilla_produktion and spielvilla_produktion != max_power_ap:
            set_power_spielvilla = get_power_spielvilla.json().get('maxPower', 0) + diff_produktion
            if set_power_spielvilla > max_power_ap:
                set_power_spielvilla = max_power_ap
        elif garage_produktion > spielvilla_produktion and spielvilla_produktion == max_power_ap:
            set_power_spielvilla = get_power_spielvilla.json().get('maxPower', 0) + diff_produktion


