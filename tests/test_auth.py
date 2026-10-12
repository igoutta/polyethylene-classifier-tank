import pytest
from fastapi.testclient import TestClient

from polyethylene_tank.app import app


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("TANK_USER", "operador")
    monkeypatch.setenv("TANK_PASSWORD", "secreto")
    with TestClient(app) as client:
        yield client


@pytest.mark.parametrize("path", ["/", "/api/status"])
def test_requires_credentials(client, path):
    response = client.get(path)
    assert response.status_code == 401
    assert response.headers["www-authenticate"].startswith("Basic")


@pytest.mark.parametrize("auth", [("operador", "mal"), ("otro", "secreto")])
def test_rejects_wrong_credentials(client, auth):
    assert client.get("/api/status", auth=auth).status_code == 401


def test_accepts_right_credentials(client):
    assert client.get("/api/status", auth=("operador", "secreto")).status_code == 200


def test_actions_are_protected(client):
    assert client.post("/api/start").status_code == 401
    assert (
        client.get("/api/status", auth=("operador", "secreto")).json()["running"]
        is False
    )
