import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings
from app.db.base import Base
from app.db.session import get_db
from app.main import app

settings = get_settings()
TEST_DB_NAME = f"{settings.postgres_db}_test"


@pytest.fixture(scope="session")
def test_engine():
    admin_url = settings.database_url.set(database="postgres")
    admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as conn:
        conn.exec_driver_sql(f'DROP DATABASE IF EXISTS "{TEST_DB_NAME}"')
        conn.exec_driver_sql(f'CREATE DATABASE "{TEST_DB_NAME}"')
    admin_engine.dispose()

    test_url = settings.database_url.set(database=TEST_DB_NAME)
    engine = create_engine(test_url)
    with engine.connect() as conn:
        conn.exec_driver_sql("CREATE EXTENSION IF NOT EXISTS vector")
        conn.commit()
    Base.metadata.create_all(bind=engine)

    yield engine

    engine.dispose()
    with admin_engine.connect() as conn:
        pass
    admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as conn:
        conn.exec_driver_sql(f'DROP DATABASE IF EXISTS "{TEST_DB_NAME}"')
    admin_engine.dispose()


@pytest.fixture()
def db_session(test_engine):
    connection = test_engine.connect()
    transaction = connection.begin()
    TestingSessionLocal = sessionmaker(bind=connection)
    session = TestingSessionLocal()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def make_user(client):
    def _make(email: str | None = None, password: str = "SuperSecret123"):
        email = email or f"{uuid.uuid4()}@example.com"
        client.post("/auth/register", json={"email": email, "password": password})
        resp = client.post("/auth/login", json={"email": email, "password": password})
        token = resp.json()["access_token"]
        return {"email": email, "password": password, "token": token,
                "headers": {"Authorization": f"Bearer {token}"}}
    return _make