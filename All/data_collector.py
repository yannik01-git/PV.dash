import asyncio
import logging
from typing import Dict, Any, Optional
import datetime
import aiohttp

import config_all
from init import APsystemsEZ1M, FEMSAPI

_LOGGER = logging.getLogger(__name__)

LATEST_FEMS: Dict[str, Dict[str, Any]] = {}
LATEST_AP: Dict[str, Dict[str, Any]] = {}


class DataCollector:
    def __init__(self, update_interval: int = config_all.UPDATE_INTERVAL, timeout: int = config_all.REQUEST_TIMEOUT):
        self.update_interval = update_interval
        self.timeout = timeout
        self._session: Optional[aiohttp.ClientSession] = None
        self._task: Optional[asyncio.Task] = None
        self._running = False

    async def _ensure_session(self):
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()

    async def fetch_fems(self, fems_conf: Dict[str, Any]) -> Dict[str, Any]:
        await self._ensure_session()
        ip = fems_conf.get("ip")
        port = fems_conf.get("port", 80)
        username = fems_conf.get("username", "x")
        password = fems_conf.get("password", "user")
        base = f"http://{ip}:{port}/rest/api"

        result: Dict[str, Any] = {"name": fems_conf.get("name"), "timestamp": datetime.datetime.utcnow().isoformat(), "raw": {}}

        try:
            endpoints = {
                "system_state": "system/state",
                "energy_storage": "storage/state",
                "grid": "grid/state",
                "production": "production/state",
                "consumption": "consumption/state",
            }

            for key, ep in endpoints.items():
                url = f"{base}/{ep}"
                async with self._session.get(url, auth=aiohttp.BasicAuth(username, password), timeout=self.timeout) as resp:
                    if resp.status == 200:
                        try:
                            j = await resp.json()
                            result["raw"][key] = j
                        except Exception:
                            result["raw"][key] = await resp.text()
                    else:
                        result["raw"][key] = {"http_status": resp.status}
        except Exception as e:
            _LOGGER.warning("FEMS %s nicht erreichbar: %s", ip, e)
            result["error"] = str(e)

        return result

    async def fetch_ap(self, ap_conf: Dict[str, Any]) -> Dict[str, Any]:
        await self._ensure_session()
        ip = ap_conf.get("ip")
        port = ap_conf.get("port", 8050)
        base = f"http://{ip}:{port}"

        result: Dict[str, Any] = {"name": ap_conf.get("name"), "timestamp": datetime.datetime.utcnow().isoformat(), "raw": {}}

        try:
            endpoints = {
                "device_info": "device/info",
                "output": "device/output",
            }

            for key, ep in endpoints.items():
                url = f"{base}/{ep}"
                async with self._session.get(url, timeout=self.timeout) as resp:
                    if resp.status == 200:
                        try:
                            j = await resp.json()
                            result["raw"][key] = j
                        except Exception:
                            result["raw"][key] = await resp.text()
                    else:
                        result["raw"][key] = {"http_status": resp.status}
        except Exception as e:
            _LOGGER.warning("AP %s nicht erreichbar: %s", ip, e)
            result["error"] = str(e)

        return result

    async def _loop(self):
        global LATEST_FEMS, LATEST_AP
        await self._ensure_session()
        while self._running:
            fems_tasks = [self.fetch_fems(cfg) for cfg in config_all.FEMS_CONFIGS]
            ap_tasks = [self.fetch_ap(cfg) for cfg in config_all.AP_CONFIGS]
            fems_results = await asyncio.gather(*fems_tasks, return_exceptions=True)
            ap_results = await asyncio.gather(*ap_tasks, return_exceptions=True)

            for cfg, res in zip(config_all.FEMS_CONFIGS, fems_results):
                name = cfg.get("name", cfg.get("ip"))
                LATEST_FEMS[name] = res if not isinstance(res, Exception) else {"error": str(res)}

            for cfg, res in zip(config_all.AP_CONFIGS, ap_results):
                name = cfg.get("name", cfg.get("ip"))
                LATEST_AP[name] = res if not isinstance(res, Exception) else {"error": str(res)}

            await asyncio.sleep(self.update_interval)

    def start_background(self, loop: Optional[asyncio.AbstractEventLoop] = None):
        if self._running:
            return
        self._running = True
        loop = loop or asyncio.get_event_loop()
        self._task = loop.create_task(self._loop())

    async def stop(self):
        self._running = False
        if self._task is not None:
            self._task.cancel()
        if self._session is not None:
            await self._session.close()

    # --- Hilfsfunktionen ---
    @staticmethod
    def total_production_power() -> float:
        total = 0.0
        for d in LATEST_AP.values():
            try:
                out = d.get("raw", {}).get("output", {})
                p = out.get("p1") or out.get("active_power") or out.get("power")
                if p is not None:
                    total += float(p)
            except Exception:
                continue

        for d in LATEST_FEMS.values():
            try:
                prod = d.get("raw", {}).get("production", {})
                if isinstance(prod, dict):
                    p = prod.get("active_power") or prod.get("ac_active_power")
                    if p is not None:
                        total += float(p)
            except Exception:
                continue
        return total

    @staticmethod
    def total_consumption_power() -> float:
        total = 0.0
        for d in LATEST_FEMS.values():
            try:
                cons = d.get("raw", {}).get("consumption", {})
                p = cons.get("active_power") or cons.get("power")
                if p is not None:
                    total += float(p)
            except Exception:
                continue
        return total

    @staticmethod
    def average_battery_soc() -> Optional[float]:
        vals = []
        for d in LATEST_FEMS.values():
            try:
                soc = d.get("raw", {}).get("energy_storage", {}).get("soc")
                if soc is not None:
                    vals.append(float(soc))
            except Exception:
                continue
        if not vals:
            return None
        return sum(vals) / len(vals)
