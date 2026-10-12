import pytest
from fastapi.testclient import TestClient

from polyethylene_tank.app import app


@pytest.fixture
def client():
    # El context manager ejecuta el lifespan (crea y cierra el hardware)
    with TestClient(app) as client:
        yield client


def test_starts_stopped(client):
    assert client.get("/api/status").json() == {"running": False, "step": "Detenido"}


def test_start_then_stop(client):
    assert client.post("/api/start").json()["running"] is True
    assert client.get("/api/status").json()["step"] == "Llenando el tanque"
    assert client.post("/api/stop").json() == {"running": False, "step": "Detenido"}


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
