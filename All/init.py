from dataclasses import dataclass
import re
import logging
import datetime
from aiohttp import ClientSession
from aiohttp.http_exceptions import HttpBadRequest
from typing import Optional, Union

_LOGGER = logging.getLogger(__name__)

class InverterReturnedError(Exception):
    """Base exception class for inverter errors"""
    pass

class FEMSReturnedError(Exception):
    """Base exception class for FEMS errors"""
    pass

# APsystems specific dataclasses
@dataclass
class ReturnDeviceInfo:
    deviceId: str
    devVer: str
    ssid: str
    ipAddr: str
    minPower: int
    maxPower: int
    isBatterySystem: bool

@dataclass
class ReturnAlarmInfo:
    offgrid: bool
    shortcircuit_1: bool
    shortcircuit_2: bool
    operating: bool

@dataclass
class ReturnOutputData:
    p1: float
    e1: float
    te1: float
    p2: float
    e2: float
    te2: float

    def __init__(self, **data):
        '''The data attribute needs to be set manually because the inverter local interface 
        may return more results than the existing data attributes (such as originalData),
          resulting in an error. '''
        self.p1 = data.get("p1", 0.0)
        self.e1 = data.get("e1", 0.0)
        self.te1 = data.get("te1", 0.0)
        self.p2 = data.get("p2", 0.0)
        self.e2 = data.get("e2", 0.0)
        self.te2 = data.get("te2", 0.0)

# FEMS specific dataclasses
@dataclass
class ReturnSystemState:
    """Systemzustand von FEMS"""
    state: int  # 0: Ok, 1: Info, 2: Warning, 3: Fault
    state_text: str

@dataclass
class ReturnEnergyStorage:
    """Energiespeicher-Daten"""
    soc: Optional[float]  # Ladezustand in %
    active_power: Optional[float]  # AC-seitige Wirkleistung in W
    reactive_power: Optional[float]  # AC-seitige Blindleistung in var
    discharge_power: Optional[float]  # Tatsächliche AC-seitige Wirkleistung in W
    active_charge_energy: Optional[float]  # Kumulierte Ladeenergie in Wh
    active_discharge_energy: Optional[float]  # Kumulierte Entladeenergie in Wh
    dc_charge_energy: Optional[float]  # Kumulierte DC-Ladeenergie in Wh
    dc_discharge_energy: Optional[float]  # Kumulierte DC-Entladeenergie in Wh

@dataclass
class ReturnGridData:
    """Netzdaten"""
    active_power: Optional[float]  # Wirkleistung am Netzanschlusspunkt in W
    min_active_power: Optional[float]  # Minimale Wirkleistung in W
    max_active_power: Optional[float]  # Maximale Wirkleistung in W
    buy_active_energy: Optional[float]  # Kumulierte Netzbezugsenergie in Wh
    sell_active_energy: Optional[float]  # Kumulierte Einspeiseenergie in Wh
    grid_mode: Optional[int]  # 1: On-Grid, 2: Off-Grid

@dataclass
class ReturnProductionData:
    """Erzeugungsdaten"""
    active_power: Optional[float]  # Wirkleistung PV-Ertrag in W
    max_active_power: Optional[float]  # Maximale Wirkleistung PV in W
    ac_active_power: Optional[float]  # Wirkleistung externe AC-Wechselrichter in W
    dc_actual_power: Optional[float]  # DC-Erzeugung Hybridwechselrichter in W
    active_energy: Optional[float]  # Kumulierte PV-Energie in Wh
    ac_active_energy: Optional[float]  # Kumulierte Energie externe WR in Wh
    dc_active_energy: Optional[float]  # Kumulierte DC-Energie in Wh

@dataclass
class ReturnConsumptionData:
    """Verbrauchsdaten"""
    active_power: Optional[float]  # Wirkleistung Verbrauch in W
    max_active_power: Optional[float]  # Maximale Wirkleistung Verbrauch in W
    active_energy: Optional[float]  # Kumulierter Verbrauch in Wh

@dataclass
class ReturnFEMSData:
    """Komplette FEMS Daten"""
    system_state: ReturnSystemState
    energy_storage: ReturnEnergyStorage
    grid: ReturnGridData
    production: ReturnProductionData
    consumption: ReturnConsumptionData
    timestamp: datetime.datetime

# APsystems regex constant
IS_BATTERY_REGEX = re.compile("^.*_b$")

class APsystemsEZ1M:
    """This class represents an EZ1 Microinverter and provides methods to interact with it
    over a network. The class allows for getting and setting various device parameters like
    power status, alarm information, device information, and power limits.
    """

    @dataclass
    class _DebounceVal:
        old_state: float = 0.0
        base_state: float = 0.0
        last_update: int = 0

    def __init__(
        self,
        ip_address: str,
        port: int = 8050,
        timeout: int = 10,
        max_power: int = 800,
        min_power: int = 30,
        session: ClientSession | None = None,
        enable_debounce: bool = False,
    ) -> None:
        """
        Initializes a new instance of the EZ1Microinverter class with the specified IP address
        and port.

        :param ip_address: The IP address of the EZ1 Microinverter.
        :param port: The port on which the microinverter's server is running. Default is 8050.
        :param timeout: The timeout for all requests. The default of 10 seconds should be plenty.
        """
        self.base_url = f"http://{ip_address}:{port}"
        self.timeout = timeout
        self.session = session
        self.max_power = max_power
        self.min_power = min_power
        self.enable_debounce = enable_debounce
        self._e1 = self._DebounceVal()
        self._e2 = self._DebounceVal()

    async def _request(self, endpoint: str, retry: int = 3) -> dict | None:
        """
        A private method to send HTTP requests to the specified endpoint of the microinverter.
        This method is used internally by other class methods to perform GET or POST requests.

        :param endpoint: The API endpoint to make the request to.
        :param retry: Number of retry attempts if the request fails.
        """
        url = f"{self.base_url}/{endpoint}"
        # Rest of the method implementation will be added later

class FEMSAPI:
    """
    Diese Klasse repräsentiert eine FENECON FEMS Anlage und stellt Methoden bereit,
    um über das Netzwerk mit ihr zu interagieren. Die Klasse ermöglicht das Abrufen
    verschiedener Systemparameter wie Speicherzustand, Netzstatus, Erzeugung und Verbrauch.
    """

    def __init__(
        self,
        ip_address: str,
        username: str = "x",
        password: str = "user",
        port: int = 80,
        timeout: int = 10,
        session: ClientSession | None = None,
    ) -> None:
        """
        Initialisiert eine neue Instanz der FEMSAPI Klasse mit der angegebenen IP-Adresse
        und Authentifizierungsdaten.

        :param ip_address: Die IP-Adresse des FEMS Systems
        :param username: Benutzername (Standard: "x", da nur Passwort-Auth verwendet wird)
        :param password: Passwort (Standard: "user" für Gast-Benutzer)
        :param port: Port für die REST/JSON-API (Standard: 80)
        :param timeout: Timeout für alle Anfragen in Sekunden (Standard: 10)
        """
        self.base_url = f"http://{ip_address}:{port}/rest/api"
        self.timeout = timeout
        self.session = session
        self.auth = (username, password)

    async def _request(self, endpoint: str, retry: int = 3) -> dict | None:
        """
        Eine private Methode zum Senden von HTTP-Anfragen an den angegebenen Endpunkt des FEMS.
        Diese Methode wird intern von anderen Klassenmethoden verwendet, um GET- oder POST-Anfragen
        durchzuführen.

        :param endpoint: Der API-Endpunkt, an den die Anfrage gesendet werden soll
        :param retry: Anzahl der Wiederholungsversuche bei Fehlschlägen
        """
        url = f"{self.base_url}/{endpoint}"
        # Rest of the method implementation will be added later