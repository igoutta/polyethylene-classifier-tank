"""API y panel web de control del tanque.

Se ejecuta con un solo worker (el hardware es único): ver `__main__.py`.
Si existe la variable TANK_PASSWORD, todo pide usuario (TANK_USER, por
defecto "admin") y contraseña con HTTP Basic.
"""

import logging
import os
import secrets
from contextlib import asynccontextmanager
from http import HTTPStatus
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from .tank import Tank

STATIC = Path(__file__).parent / "static"
REALM = "Tanque clasificador"

log = logging.getLogger(__name__)
basic = HTTPBasic(auto_error=False, realm=REALM)


def _coincide(dado, esperado):
    return secrets.compare_digest(dado.encode(), esperado.encode())


def autenticar(credenciales: Annotated[HTTPBasicCredentials | None, Depends(basic)]):
    clave = os.environ.get("TANK_PASSWORD")
    if not clave:
        return  # sin contraseña configurada el panel queda abierto
    if credenciales is not None:
        usuario_ok = _coincide(
            credenciales.username, os.environ.get("TANK_USER", "admin")
        )
        clave_ok = _coincide(credenciales.password, clave)
        if usuario_ok and clave_ok:
            return
    raise HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail="Usuario o contraseña incorrectos",
        headers={"WWW-Authenticate": f'Basic realm="{REALM}"'},
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not os.environ.get("TANK_PASSWORD"):
        log.warning("TANK_PASSWORD no está definida: el panel no pide contraseña")
    app.state.tank = Tank()
    try:
        yield
    finally:
        app.state.tank.close()


app = FastAPI(
    title="Tanque clasificador de polietileno",
    lifespan=lifespan,
    dependencies=[Depends(autenticar)],
)


def estado(tank: Tank):
    return {"running": tank.running, "step": tank.step, "error": tank.error}


# Los endpoints son sync a propósito: FastAPI los ejecuta en un hilo y
# stop() (que mueve servos unos segundos) no bloquea el resto del servidor.
@app.get("/api/status")
def status():
    return estado(app.state.tank)


@app.post("/api/start")
def start():
    app.state.tank.start()
    return estado(app.state.tank)


@app.post("/api/stop")
def stop():
    app.state.tank.stop()
    return estado(app.state.tank)


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")
