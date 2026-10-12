"""Tiempos del ciclo, validados (incluidos los que llegan desde el panel)."""

import logging

from pydantic import BaseModel, Field, ValidationError

from .config import (
    TIEMPO_DESFOGUE_SEC,
    TIEMPO_LIMPIEZA_SEC,
    TIEMPO_LLENADO_SEC,
    TIEMPO_MAX_SEC,
)
from .files import write_atomic

log = logging.getLogger(__name__)


class Tiempos(BaseModel):
    """Duración de cada etapa en segundos."""

    llenado: float = Field(default=TIEMPO_LLENADO_SEC, gt=0, le=TIEMPO_MAX_SEC)
    limpieza: float = Field(default=TIEMPO_LIMPIEZA_SEC, gt=0, le=TIEMPO_MAX_SEC)
    desfogue: float = Field(default=TIEMPO_DESFOGUE_SEC, gt=0, le=TIEMPO_MAX_SEC)


def cargar(path):
    """Tiempos guardados en `path`, o los de config.py si no hay o no valen."""
    try:
        return Tiempos.model_validate_json(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return Tiempos()
    except (OSError, ValidationError) as exc:
        log.warning("Tiempos en %s no válidos, se usan los de config: %s", path, exc)
        return Tiempos()


def guardar(path, tiempos):
    write_atomic(path, tiempos.model_dump_json(indent=2))
