# Datei zum rechnen der Anzeigewerte für die GUI

# =============================================================================

import asyncio
import datetime
import aiohttp
import logging

import config_all

_LOGGER = logging.getLogger(__name__)

# -------------------------
# Dynamisch erzeugte Variablen für FEMS und AP
# -------------------------
fems_values = {}   # z.B. fems_values["fems1"]["production"]
ap_values = {}     # z.B. ap_values["ap1"]["output"]

last_update = None


async def fetch_fems(fems_conf, index: int):
    """Abfrage einer FEMS-Anlage und Speicherung in fems_values[fems{index}]"""
    key = f"fems{index}"
    fems_values[key] = {}

    ip = fems_conf.get("ip")
    port = fems_conf.get("port", 80)
    username = fems_conf.get("username", "x")
    password = fems_conf.get("password", "user")
    base = f"http://{ip}:{port}/rest/api"

    endpoints = {
        "system_state": "system/state",
        "energy_storage": "storage/state",
        "grid": "grid/state",
        "production": "production/state",
        "consumption": "consumption/state",
    }

    async with aiohttp.ClientSession() as session:
        try:
            for name, ep in endpoints.items():
                url = f"{base}/{ep}"
                async with session.get(url, auth=aiohttp.BasicAuth(username, password), timeout=5) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                    else:
                        data = {"error": f"HTTP {resp.status}"}

                fems_values[key][name] = data

        except Exception as e:
            _LOGGER.warning("Fehler beim Abfragen von FEMS %s: %s", ip, e)
            fems_values[key]["error"] = str(e)


async def fetch_ap(ap_conf, index: int):
    """Abfrage eines APsystems-Geräts und Speicherung in ap_values[ap{index}]"""
    key = f"ap{index}"
    ap_values[key] = {}

    ip = ap_conf.get("ip")
    port = ap_conf.get("port", 8050)
    base = f"http://{ip}:{port}"

    endpoints = {
        "device_info": "device/info",
        "output": "device/output",
    }

    async with aiohttp.ClientSession() as session:
        try:
            for name, ep in endpoints.items():
                url = f"{base}/{ep}"
                async with session.get(url, timeout=5) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                    else:
                        data = {"error": f"HTTP {resp.status}"}

                ap_values[key][name] = data

        except Exception as e:
            _LOGGER.warning("Fehler beim Abfragen von AP %s: %s", ip, e)
            ap_values[key]["error"] = str(e)


async def update_loop():
    """Hintergrundschleife, die regelmäßig alle Werte abfragt"""
    global last_update

    while True:
        fems_tasks = [fetch_fems(cfg, i + 1) for i, cfg in enumerate(config_all.FEMS_CONFIGS)]
        ap_tasks = [fetch_ap(cfg, i + 1) for i, cfg in enumerate(config_all.AP_CONFIGS)]

        await asyncio.gather(*fems_tasks, *ap_tasks)

        last_update = datetime.datetime.utcnow().isoformat()

        await asyncio.sleep(config_all.UPDATE_INTERVAL)


def start_background(loop=None):
    """Startet die Update-Schleife im Hintergrund"""
    loop = loop or asyncio.get_event_loop()
    loop.create_task(update_loop())


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    start_background(loop)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("Beendet.")
