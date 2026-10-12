"""Último peso de la balanza, compartido entre su servicio y el panel.

La balanza escribe cada lectura en un archivo en memoria (/dev/shm en la Pi)
para no desgastar la tarjeta SD; el panel lo muestra solo si es reciente.
"""

import json
from time import time

from .config import PESO_FILE, PESO_MAX_EDAD_SEC
from .files import write_atomic


def publicar(peso, path=PESO_FILE):
    write_atomic(path, json.dumps({"peso": peso, "t": time()}))


def leer(path=PESO_FILE, max_edad=PESO_MAX_EDAD_SEC):
    """Último peso, o None si la balanza no publicó en los últimos segundos."""
    try:
        dato = json.loads(path.read_text(encoding="utf-8"))
        edad = time() - dato["t"]
        peso = float(dato["peso"])
    except (OSError, ValueError, KeyError, TypeError):
        return None
    return peso if edad <= max_edad else None
