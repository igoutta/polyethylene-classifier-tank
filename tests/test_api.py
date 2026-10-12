import pytest
from fastapi.testclient import TestClient

from polyethylene_tank.app import app
from polyethylene_tank.config import TIEMPOS_FILE
from polyethylene_tank.weight import publicar


@pytest.fixture
def client():
    # El context manager ejecuta el lifespan (crea y cierra el hardware)
    with TestClient(app) as client:
        yield client


def test_starts_stopped(client):
    assert client.get("/api/status").json() == {
        "running": False,
        "step": "Detenido",
        "error": None,
        "ciclos": 0,
        "ultimo_ciclo": None,
        "peso": None,
    }


def test_start_then_stop(client):
    assert client.post("/api/start").json()["running"] is True
    assert client.get("/api/status").json()["step"] == "Llenando el tanque"
    stopped = client.post("/api/stop").json()
    assert stopped["running"] is False
    assert stopped["step"] == "Detenido"


def test_start_twice_is_safe(client):
    client.post("/api/start")
    assert client.post("/api/start").json()["running"] is True
    client.post("/api/stop")


def test_stop_when_idle_is_safe(client):
    assert client.post("/api/stop").json()["running"] is False


def test_can_restart_after_stop(client):
    client.post("/api/start")
    client.post("/api/stop")
    assert client.post("/api/start").json()["running"] is True
    client.post("/api/stop")


def test_index_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "COMENZAR" in response.text


def test_default_timings(client):
    assert client.get("/api/tiempos").json() == {
        "llenado": 15,
        "limpieza": 60,
        "desfogue": 15,
    }


def test_change_timings_saves_and_applies_them(client):
    nuevos = {"llenado": 20, "limpieza": 45.5, "desfogue": 10}
    assert client.put("/api/tiempos", json=nuevos).json() == nuevos
    assert client.get("/api/tiempos").json() == nuevos
    assert TIEMPOS_FILE.exists()


def test_saved_timings_survive_a_restart():
    nuevos = {"llenado": 20, "limpieza": 30, "desfogue": 10}
    with TestClient(app) as client:
        client.put("/api/tiempos", json=nuevos)
    with TestClient(app) as reiniciado:  # el primero ya liberó los pines
        assert reiniciado.get("/api/tiempos").json() == nuevos


@pytest.mark.parametrize("llenado", [0, -5, 601, "mucho"])
def test_invalid_timings_are_rejected(client, llenado):
    response = client.put(
        "/api/tiempos", json={"llenado": llenado, "limpieza": 60, "desfogue": 15}
    )
    assert response.status_code == 422
    assert not TIEMPOS_FILE.exists()


def test_status_shows_the_scale_weight(client):
    publicar(123.4)
    assert client.get("/api/status").json()["peso"] == 123.4
