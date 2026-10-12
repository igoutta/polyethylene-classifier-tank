"""API y panel web de control del tanque.

Se ejecuta con un solo worker (el hardware es único): ver `__main__.py`.
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from .tank import Tank

STATIC = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.tank = Tank()
    try:
        yield
    finally:
        app.state.tank.close()


app = FastAPI(title="Tanque clasificador de polietileno", lifespan=lifespan)


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
