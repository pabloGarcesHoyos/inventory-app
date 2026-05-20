from collections.abc import Callable
from typing import Any

from sqlalchemy.orm import Session

from src.models.user import ROLE_OPERADOR, User


def test_pu_001_creacion_exitosa_de_usuario(
    create_user: Callable[..., Any],
) -> None:
    response = create_user(
        nombre="Pablo Garces",
        email="pablo@eam.edu.co",
    )

    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["email"] == "pablo@eam.edu.co"
    assert data["rol"] == ROLE_OPERADOR
    assert "password" not in data
    assert "hashed_password" not in data


def test_pu_002_rechaza_usuario_con_email_duplicado(
    create_user: Callable[..., Any],
    db_session: Session,
) -> None:
    first_response = create_user(email="duplicado@eam.edu.co")
    second_response = create_user(
        nombre="Usuario Repetido",
        email="duplicado@eam.edu.co",
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    users_count = (
        db_session.query(User)
        .filter(User.email == "duplicado@eam.edu.co")
        .count()
    )
    assert users_count == 1
