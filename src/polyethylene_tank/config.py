"""Pines (numeración J8 de gpiozero), tiempos del ciclo y rutas de estado."""

import os
from pathlib import Path

# Entradas. Los botones van entre el pin y GND (pull-up interno)
INICIAR = "J8:37"
PARAR = "J8:35"  # parada de emergencia física: no depende del panel
BOTONES_BOUNCE_SEC = 0.05
FIN_CARRERA = "J8:19"
# gpiozero mide el antirrebote en segundos: antes había 5 (cinco segundos)
FIN_CARRERA_BOUNCE_SEC = 0.005

# Relés de las bombas
RELE_LLENADO = "J8:7"
RELE_CORRIENTE = "J8:11"

# Motor NEMA
NEMA_STEP = "J8:3"
NEMA_DIR = "J8:5"

# Servos (PWM)
SAPO = "J8:33"
TUNEL = "J8:32"

# Tiempos del ciclo (segundos), valores por defecto
TIEMPO_LLENADO_SEC = 15  # máximo: si el sensor no detecta el tanque lleno, error
TIEMPO_LIMPIEZA_SEC = 60
TIEMPO_DESFOGUE_SEC = 15
TIEMPO_MAX_SEC = 600  # tope para cualquier tiempo, evita errores de tipeo

# Estado guardado en disco (tiempos fijados desde el panel)
STATE_DIR = Path(
    os.environ.get(
        "TANK_STATE_DIR", Path.home() / ".local" / "state" / "polyethylene-tank"
    )
)
TIEMPOS_FILE = STATE_DIR / "tiempos.json"

# Balanza HX711 (pines BCM, no la numeración J8) y calibración
SCALE_DATA = 9  # pin físico 21
SCALE_CLOCK = 11  # pin físico 23
SCALE_REFERENCE_UNIT = -7627  # cuentas por gramo (el signo depende del cableado)

# Registro (systemd/journalctl ya añade la fecha y hora)
LOG_FORMAT = "%(levelname)s %(name)s: %(message)s"

# Servidor web
HOST = "0.0.0.0"
PORT = 8080
