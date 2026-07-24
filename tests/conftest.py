import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


TEST_DATABASE = Path(__file__).parent / "test.db"
if TEST_DATABASE.exists():
    TEST_DATABASE.unlink()
os.environ["INTELLIMED_DATABASE_URL"] = f"sqlite:///{TEST_DATABASE}"
os.environ["INTELLIMED_SESSION_SECRET"] = "test-session-secret"
os.environ["INTELLIMED_ENV"] = "testing"
os.environ.pop("INTELLIMED_ADMIN_EMAIL", None)
os.environ.pop("INTELLIMED_ADMIN_PASSWORD", None)

from app.db import engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as test_client:
        yield test_client
    engine.dispose()
    TEST_DATABASE.unlink(missing_ok=True)


def csrf(client: TestClient, path: str = "/") -> str:
    response = client.get(path)
    marker = 'name="csrf" value="'
    return response.text.split(marker, 1)[1].split('"', 1)[0]
