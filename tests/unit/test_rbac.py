from collections.abc import Callable
from typing import Any

from fastapi.testclient import TestClient

from src.models.user import ROLE_ADMINISTRADOR, ROLE_OPERADOR, STATUS_ACTIVO
from src.models.user import STATUS_INACTIVO, User


def test_pu_003_asignacion_de_rol_a_usuario(
    client: TestClient,
    create_user: Callable[..., Any],
    auth_headers: Callable[[str, str], dict[str, str]],
) -> None:
    create_user(
        nombre="Admin",
        email="admin@eam.edu.co",
        rol=ROLE_ADMINISTRADOR,
    )
    target_response = create_user(
        nombre="Operador",
        email="operador@eam.edu.co",
        rol=ROLE_OPERADOR,
    )
    target_user_id = target_response.json()["id"]

    response = client.put(
        f"/api/usuarios/{target_user_id}/rol",
        json={"rol": ROLE_ADMINISTRADOR},
        headers=auth_headers("admin@eam.edu.co"),
    )

    assert response.status_code == 200
    assert response.json()["rol"] == ROLE_ADMINISTRADOR


def test_pu_014_operador_no_puede_eliminar_usuario(
    client: TestClient,
    create_user: Callable[..., Any],
    auth_headers: Callable[[str, str], dict[str, str]],
    get_user_from_db: Callable[[int], User | None],
) -> None:
    create_user(
        nombre="Operador",
        email="operador-rbac@eam.edu.co",
        rol=ROLE_OPERADOR,
    )
    target_response = create_user(
        nombre="Usuario Objetivo",
        email="objetivo@eam.edu.co",
        rol=ROLE_OPERADOR,
    )
    target_user_id = target_response.json()["id"]

    response = client.delete(
        f"/api/usuarios/{target_user_id}",
        headers=auth_headers("operador-rbac@eam.edu.co"),
    )

    assert response.status_code == 403
    target_user = get_user_from_db(target_user_id)
    assert target_user is not None
    assert target_user.estado == STATUS_ACTIVO


def test_pu_017_eliminacion_logica_de_usuario(
    client: TestClient,
    create_user: Callable[..., Any],
    auth_headers: Callable[[str, str], dict[str, str]],
    get_user_from_db: Callable[[int], User | None],
) -> None:
    create_user(
        nombre="Admin",
        email="admin-delete@eam.edu.co",
        rol=ROLE_ADMINISTRADOR,
    )
    target_response = create_user(
        nombre="Usuario Inactivo",
        email="inactivo@eam.edu.co",
        rol=ROLE_OPERADOR,
    )
    target_user_id = target_response.json()["id"]

    delete_response = client.delete(
        f"/api/usuarios/{target_user_id}",
        headers=auth_headers("admin-delete@eam.edu.co"),
    )

    assert delete_response.status_code == 200
    assert delete_response.json()["estado"] == STATUS_INACTIVO
    target_user = get_user_from_db(target_user_id)
    assert target_user is not None
    assert target_user.estado == STATUS_INACTIVO

    login_response = client.post(
        "/api/auth/login",
        json={"email": "inactivo@eam.edu.co", "password": "Segura#123"},
    )

    assert login_response.status_code == 401
