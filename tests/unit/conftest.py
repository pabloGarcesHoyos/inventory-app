from collections.abc import Callable, Generator
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from src.core.database import Base, get_db
from src.main import app
from src.models.user import User


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session_local = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )
    Base.metadata.create_all(bind=engine)
    db = testing_session_local()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app)

    try:
        yield test_client
    finally:
        app.dependency_overrides.clear()
        test_client.close()


@pytest.fixture()
def create_user(client: TestClient) -> Callable[..., Any]:
    def _create_user(
        *,
        nombre: str = "Usuario Prueba",
        email: str = "usuario@eam.edu.co",
        password: str = "Segura#123",
        rol: str | None = None,
    ) -> Any:
        payload = {
            "nombre": nombre,
            "email": email,
            "password": password,
        }
        if rol is not None:
            payload["rol"] = rol

        return client.post("/api/usuarios", json=payload)

    return _create_user


@pytest.fixture()
def auth_headers(client: TestClient) -> Callable[[str, str], dict[str, str]]:
    def _auth_headers(email: str, password: str = "Segura#123") -> dict[str, str]:
        response = client.post(
            "/api/auth/login",
            json={"email": email, "password": password},
        )
        assert response.status_code == 200
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    return _auth_headers


@pytest.fixture()
def get_user_from_db(db_session: Session) -> Callable[[int], User | None]:
    def _get_user_from_db(user_id: int) -> User | None:
        db_session.expire_all()
        return db_session.get(User, user_id)

    return _get_user_from_db
