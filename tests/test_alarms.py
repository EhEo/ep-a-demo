"""Tests for the alarms router."""
import time

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

import app.routers.alarms as alarms_mod
from app.routers.alarms import lifespan, router

FUTURE = "2030-01-01T00:00:00Z"
PAST = "2000-01-01T00:00:00Z"


@pytest.fixture(autouse=True)
def reset_store():
    """Wipe module-level state between tests."""
    alarms_mod._store.clear()
    alarms_mod._next_id = 1
    yield
    alarms_mod._store.clear()
    alarms_mod._next_id = 1


@pytest.fixture()
def client():
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


# --- POST /alarms ---

def test_create_alarm_returns_201(client):
    resp = client.post("/alarms", json={"trigger_at": FUTURE, "message": "wake up"})
    assert resp.status_code == 201


def test_create_alarm_body(client):
    resp = client.post("/alarms", json={"trigger_at": FUTURE, "message": "wake up"})
    data = resp.json()
    assert data["id"] == 1
    assert data["message"] == "wake up"
    assert "2030-01-01" in data["trigger_at"]
    assert data["fired"] is False


def test_create_alarm_ids_increment(client):
    r1 = client.post("/alarms", json={"trigger_at": FUTURE, "message": "a"})
    r2 = client.post("/alarms", json={"trigger_at": FUTURE, "message": "b"})
    assert r1.json()["id"] == 1
    assert r2.json()["id"] == 2


def test_create_alarm_missing_field_returns_422(client):
    resp = client.post("/alarms", json={"message": "no time"})
    assert resp.status_code == 422


# --- GET /alarms ---

def test_list_alarms_empty(client):
    assert client.get("/alarms").json() == []


def test_list_alarms_returns_all(client):
    client.post("/alarms", json={"trigger_at": FUTURE, "message": "a"})
    client.post("/alarms", json={"trigger_at": FUTURE, "message": "b"})
    resp = client.get("/alarms")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_list_alarms_after_delete(client):
    client.post("/alarms", json={"trigger_at": FUTURE, "message": "a"})
    client.post("/alarms", json={"trigger_at": FUTURE, "message": "b"})
    client.delete("/alarms/1")
    items = client.get("/alarms").json()
    assert len(items) == 1
    assert items[0]["id"] == 2


# --- DELETE /alarms/{id} ---

def test_delete_alarm_returns_204(client):
    client.post("/alarms", json={"trigger_at": FUTURE, "message": "bye"})
    resp = client.delete("/alarms/1")
    assert resp.status_code == 204


def test_delete_alarm_removes_it(client):
    client.post("/alarms", json={"trigger_at": FUTURE, "message": "bye"})
    client.delete("/alarms/1")
    assert client.get("/alarms").json() == []


def test_delete_nonexistent_returns_404(client):
    resp = client.delete("/alarms/999")
    assert resp.status_code == 404


def test_delete_already_deleted_returns_404(client):
    client.post("/alarms", json={"trigger_at": FUTURE, "message": "once"})
    client.delete("/alarms/1")
    resp = client.delete("/alarms/1")
    assert resp.status_code == 404


# --- Lifecycle / dispatcher ---

def test_dispatcher_fires_past_alarm():
    app = FastAPI(lifespan=lifespan)
    app.include_router(router)

    with TestClient(app) as c:
        resp = c.post("/alarms", json={"trigger_at": PAST, "message": "overdue"})
        assert resp.status_code == 201
        alarm_id = resp.json()["id"]

        time.sleep(1.1)

        items = c.get("/alarms").json()
        alarm = next(a for a in items if a["id"] == alarm_id)
        assert alarm["fired"] is True
