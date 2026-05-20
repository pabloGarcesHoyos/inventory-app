from collections.abc import Callable
from typing import Any

from fastapi.testclient import TestClient


def test_login_retorna_jwt(
    client: TestClient,
    create_user: Callable[..., Any],
) -> None:
    create_user(email="login@eam.edu.co")

    response = client.post(
        "/api/auth/login",
        json={"email": "login@eam.edu.co", "password": "Segura#123"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["access_token"]
    assert data["token_type"] == "bearer"


def test_pu_013_token_jwt_invalido_en_endpoint_protegido(
    client: TestClient,
) -> None:
    response = client.get(
        "/api/usuarios/me",
        headers={"Authorization": "Bearer token-invalido"},
    )

    assert response.status_code == 401
