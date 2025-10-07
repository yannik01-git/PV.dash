import requests
from pages import Settings

# --------------------------------------------------------
# 🔧 IP-Adressen & Authentifizierung
# --------------------------------------------------------
FEMS_IP = "192.168.188.66"
GARAGE_IP = "192.168.188.63"
SPIELVILLA_IP = "192.168.188.122"

USER = "Gast"
PASSWORD = "user"

# Gemeinsame Session
session = requests.Session()
session.auth = (USER, PASSWORD)

# --------------------------------------------------------
# 🧩 Hilfsfunktionen
# --------------------------------------------------------
def safe_get_json(url, timeout=3):
    """Sichere JSON-Abfrage, gibt {} bei Fehler zurück"""
    try:
        r = session.get(url, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except Exception:
        return {}

def safe_get_value(url, timeout=3):
    """Holt einen einzelnen JSON-Wert, gibt None bei Fehler zurück"""
    try:
        r = session.get(url, timeout=timeout)
        r.raise_for_status()
        return r.json().get("value", None)
    except Exception:
        return None


# --------------------------------------------------------
# 🔋 FEMS-Daten
# --------------------------------------------------------
def fetch_fems_data():
    """Holt aktuelle FEMS-Daten und gibt sie als Dict zurück"""
    data = {"online": False}

    try:
        response = requests.get(f"http://{FEMS_IP}:80", timeout=3)
        response.raise_for_status()
        data["online"] = True
            # Werte abfragen
        prefix = f"http://{USER}:{PASSWORD}@{FEMS_IP}:80/rest/channel/_sum/"
        data["charging_state"] = safe_get_value(prefix + "EssSoc")
        data["production_power"] = safe_get_value(prefix + "ProductionActivePower")
        data["grid_power"] = safe_get_value(prefix + "GridActivePower")
        data["battery_power"] = safe_get_value(prefix + "EssActivePower")
        data["consumption"] = safe_get_value(prefix + "ConsumptionActivePower")
        data["status"] = safe_get_value(prefix + "State")
        data["grid_mode"] = safe_get_value(prefix + "GridMode")

        consumption = data["consumption"] or 0
        if consumption < 0:
            data["balkon"] = abs(consumption)
            data["consumption"] = 0
        else:
            data["balkon"] = 0
        return data
    except requests.exceptions.RequestException:
        return data




# --------------------------------------------------------
# ☀️ AP-Garage
# --------------------------------------------------------
def fetch_garage_data():
    """Holt aktuelle Daten von der Garage-AP"""
    data = {"online": False}
    try:
        response = requests.get(f"http://{GARAGE_IP}:8050", timeout=3)
        response.raise_for_status()
        data["online"] = True
        data["ap"] = safe_get_json(f"http://{GARAGE_IP}:8050/get_output_data")
        data["max_power"] = safe_get_json(f"http://{GARAGE_IP}:8050/getMaxPower")
        return data
    except requests.exceptions.RequestException:
        data["online"] = False
        data["ap"] = 0
        data["max_power"] = 0   
        return data

    


# --------------------------------------------------------
# 🏠 AP-Spielvilla
# --------------------------------------------------------
def fetch_spielvilla_data():
    """Holt aktuelle Daten von der Spielvilla-AP"""
    data = {"online": False}

    try:
        response = requests.get(f"http://{SPIELVILLA_IP}:8050", timeout=2)
        response.raise_for_status()
        data["online"] = True
        data["ap"] = safe_get_json(f"http://{SPIELVILLA_IP}:8050/get_output_data")
        data["max_power"] = safe_get_json(f"http://{SPIELVILLA_IP}:8050/getMaxPower")
        return data
    except requests.exceptions.RequestException:
        data["online"] = False
        data["ap"] = 0
        data["max_power"] = 0
        return data

    


# --------------------------------------------------------
# 🧮 Kombinierte Gesamtwerte (optional)
# --------------------------------------------------------
def fetch_combined_data():
    """
    Holt alle drei Datenquellen und berechnet kombinierte Kennzahlen.
    Gibt ein Dict zurück:
        {
            "fems": {...},
            "garage": {...},
            "spielvilla": {...},
            "pv_total": ...,
            "consumption_total": ...,
        }
    """
    fems = fetch_fems_data()
    garage = fetch_garage_data()
    spielvilla = fetch_spielvilla_data()

    pv_garage = garage["ap"].get("p1", 0) + garage["ap"].get("p2", 0) if garage["online"] else 0
    pv_spielvilla = spielvilla["ap"].get("p1", 0) + spielvilla["ap"].get("p2", 0) if spielvilla["online"] else 0
    pv_total = pv_garage + pv_spielvilla

    consumption = fems["consumption"] or 0
    consumption_total = (consumption - pv_total or 0) if fems["online"] else 0
    total_data = {
        "fems": fems,
        "garage": garage,
        "spielvilla": spielvilla,
        "pv_total": pv_total,
        "consumption_total": consumption_total,
    }
    return total_data


# --------------------------------------------------------
# Regelung der Max Leistung der AP-Systeme
# --------------------------------------------------------
minPower = 30
maxPower = 800

garage = fetch_garage_data()
spielvilla = fetch_spielvilla_data()
ap = fetch_combined_data()

garage_produktion = garage["ap"].get("p1", 0) + garage["ap"].get("p2", 0) if garage["online"] else 0
spielvilla_produktion = spielvilla["ap"].get("p1", 0) + spielvilla["ap"].get("p2", 0) if spielvilla["online"] else 0

if Settings.regelung:
    # AP-Regelung nach unten 
# Beide Module online
    if spielvilla["online"] and garage["online"]:
        if  ap["pv_total"] > 800:
            diff_produktion = ap["pv_total"] - maxPower
            if garage_produktion >= spielvilla_produktion and garage_produktion != minPower:
                set_power_garage = garage["max_power"] - diff_produktion
                if set_power_garage < minPower:
                    set_power_garage = minPower
            elif garage_produktion >= spielvilla_produktion and garage_produktion == minPower:
                set_power_spielvilla = spielvilla["max_power"] - diff_produktion

            elif garage_produktion < spielvilla_produktion and spielvilla_produktion != minPower:
                set_power_spielvilla = spielvilla["max_power"] - diff_produktion
                if set_power_spielvilla < minPower:
                    set_power_spielvilla = minPower
            elif garage_produktion < spielvilla_produktion and spielvilla_produktion == minPower:
                set_power_spielvilla = spielvilla["max_power"] - diff_produktion

        # AP-Regelung nach oben
        # Beide Module online
        elif ap["pv_total"] < 750:
            diff_produktion =  maxPower - ap["pv_total"]
            if garage_produktion <= spielvilla_produktion and garage_produktion != maxPower:
                set_power_garage = garage["max_power"] + diff_produktion
                if set_power_garage > maxPower:
                    set_power_garage = maxPower
            elif garage_produktion <= spielvilla_produktion and garage_produktion == maxPower:
                set_power_spielvilla = spielvilla["max_power"] + diff_produktion

            elif garage_produktion > spielvilla_produktion and spielvilla_produktion != maxPower:
                set_power_spielvilla = spielvilla["max_power"] + diff_produktion
                if set_power_spielvilla > maxPower:
                    set_power_spielvilla = maxPower
            elif garage_produktion > spielvilla_produktion and spielvilla_produktion == maxPower:
                set_power_spielvilla = spielvilla["max_power"] + diff_produktion