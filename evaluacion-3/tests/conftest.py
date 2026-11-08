import pytest
from fastapi.testclient import TestClient

from src.database import Database
from src.main import DEMO_TOKEN_SUBJECTS, create_app
from src.seed import seed


@pytest.fixture
def database(tmp_path):
    db = Database(tmp_path / "test.sqlite3")
    seed(db)
    return db


@pytest.fixture
def client(database):
    app = create_app(database.path)
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def auth():
    def make(token="demo-pi-alice"):
        return {"Authorization": f"Bearer {token}"}

    return make


@pytest.fixture
def token_subjects():
    return DEMO_TOKEN_SUBJECTS
