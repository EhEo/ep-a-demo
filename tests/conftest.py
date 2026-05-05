"""Shared pytest fixtures — function-scoped TestClient for items router."""
import pytest
from fastapi.testclient import TestClient

from app.routers.items import router


@pytest.fixture(scope="function")
def client():
    return TestClient(router)
