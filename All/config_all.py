# FENECON FEMS Konfiguration
# ===========================
# 
# Diese Datei enthält die Konfiguration für Ihre FENECON FEMS Systeme.
# Passen Sie die Werte entsprechend Ihrer Installation an.

# FEMS System Konfiguration
# Jedes System benötigt folgende Angaben:
# - name: Ein beschreibender Name für das System
# - ip: Die IP-Adresse des FEMS Systems
# - username: Benutzername (meist "x", da nur Passwort verwendet wird)
# - password: Passwort (Standard: "user" für Gast-Benutzer)
# - port: REST API Port (Standard: 80)

# Beispielkonfiguration:
FEMS_CONFIGS = [
    {
        "name": "FEMS Hauptanlage",
        "ip": "192.168.188.66",  # ÄNDERN SIE DIESE IP-ADRESSE!
        "username": "Gast",
        "password": "user",
        "port": 80
    },
    # Weitere FEMS-Anlagen können hier hinzugefügt werden:
    # {
    #     "name": "FEMS Nebenanlage",
    #     "ip": "192.168.0.24",
    #     "username": "x", 
    #     "password": "user",
    #     "port": 80
    # },
]

# AP Systems EZ1 Konfiguration
# ===========================
#
# Diese Datei enthält die Konfiguration für Ihre AP Systems EZ1 Inverter.
# Passen Sie die Werte entsprechend Ihrer Installation an.

# AP System Konfiguration
# Jedes System benötigt folgende Angaben:
# - name: Ein beschreibender Name für das System
# - ip: Die IP-Adresse des AP Systems
# - port: REST API Port (Standard: 80)

# Beispielkonfiguration:
AP_CONFIGS = [
    {
        "name": "Garage",
        "ip": "192.168.188.63",
        "port": 8050
    },
    {
        "name": "Spielvilla",
        "ip": "192.168.188.122",  
        "port": 8050
    },
    # Weitere AP-Systeme können hier hinzugefügt werden:
    # {
    #     "name": "AP System Nebenanlage",
    #     "ip": "192.168.0.24",
    #     "port": 80
    # },
]

# Update-Intervall in Sekunden (häufigere Updates für bessere Datenaktualität)
UPDATE_INTERVAL = 10

# Timeout für Anfragen an FEMS in Sekunden
REQUEST_TIMEOUT = 10

# Web Monitor Port
WEB_MONITOR_PORT = 5001

# =============================================================================
# WICHTIGE HINWEISE:
# =============================================================================
# 
# 1. IP-ADRESSE ANPASSEN:
#    Ändern Sie die IP-Adresse "192.168.0.23" auf die tatsächliche 
#    IP-Adresse Ihres FEMS Systems!
#
# 2. PASSWORT PRÜFEN:
#    Das Standard-Passwort für den Gast-Benutzer ist "user".
#    Falls Sie ein anderes Passwort verwenden, ändern Sie es entsprechend.
#
# 3. MEHRERE SYSTEME:
#    Sie können mehrere FEMS-Systeme überwachen, indem Sie weitere
#    Einträge in der FEMS_CONFIGS Liste hinzufügen.
#
# 4. NETZWERK PRÜFEN:
#    Stellen Sie sicher, dass:
#    - Ihr Computer mit dem gleichen Netzwerk wie das FEMS verbunden ist
#    - Port 80 am FEMS nicht durch eine Firewall blockiert wird
#    - Die REST-API im FEMS aktiviert ist
#
# =============================================================================

## Konfiguration für die GUI

showGui = True
showDashboard = False
showDetail = True
showAP = True
showFlowBottom = False

webGui = True
localGui = True