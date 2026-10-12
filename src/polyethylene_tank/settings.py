"""Tiempos del ciclo, validados (incluidos los que llegan desde el panel)."""

from pydantic import BaseModel, Field

from .config import (
    TIEMPO_DESFOGUE_SEC,
    TIEMPO_LIMPIEZA_SEC,
    TIEMPO_LLENADO_SEC,
    TIEMPO_MAX_SEC,
)


class Tiempos(BaseModel):
    """Duración de cada etapa en segundos."""

    llenado: float = Field(default=TIEMPO_LLENADO_SEC, gt=0, le=TIEMPO_MAX_SEC)
    limpieza: float = Field(default=TIEMPO_LIMPIEZA_SEC, gt=0, le=TIEMPO_MAX_SEC)
    desfogue: float = Field(default=TIEMPO_DESFOGUE_SEC, gt=0, le=TIEMPO_MAX_SEC)
