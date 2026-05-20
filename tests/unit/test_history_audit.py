from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.exceptions.movement_exceptions import OperacionNoPermitidaException
from src.models.movement import MOVEMENT_TYPE_ENTRADA, MOVEMENT_TYPE_SALIDA, Movement
from src.models.user import ROLE_ADMINISTRADOR, ROLE_OPERADOR
from src.services import movement_service


def _headers_for_role(
    create_user: Callable[..., Any],
    auth_headers: Callable[[str, str], dict[str, str]],
    *,
    role: str,
    email: str,
) -> dict[str, str]:
    response = create_user(
        nombre=f"Usuario {role}",
        email=email,
        rol=role,
    )
    assert response.status_code == 201
    return auth_headers(email)


def _create_product(client: TestClient, headers: dict[str, str]) -> int:
    response = client.post(
        "/api/productos",
        json={
            "nombre": "Resma de Papel",
            "sku": "PAP-HIST-001",
            "categoria": "INSUMOS",
            "stock_inicial": 0,
            "stock_minimo": 10,
            "unidad": "unidades",
        },
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_pu_011_historial_de_movimientos_por_producto(
    client: TestClient,
    create_user: Callable[..., Any],
    auth_headers: Callable[[str, str], dict[str, str]],
) -> None:
    headers = _headers_for_role(
        create_user,
        auth_headers,
        role=ROLE_OPERADOR,
        email="operador-historial@eam.edu.co",
    )
    product_id = _create_product(client, headers)
    base_time = datetime(2026, 5, 20, 8, 0, tzinfo=UTC)

    movements = [
        (
            "/api/movimientos/entrada",
            {
                "producto_id": product_id,
                "cantidad": 30,
                "fecha": base_time.isoformat(),
            },
        ),
        (
            "/api/movimientos/entrada",
            {
                "producto_id": product_id,
                "cantidad": 20,
                "fecha": (base_time + timedelta(minutes=1)).isoformat(),
            },
        ),
        (
            "/api/movimientos/salida",
            {
                "producto_id": product_id,
                "cantidad": 10,
                "fecha": (base_time + timedelta(minutes=2)).isoformat(),
            },
        ),
    ]
    for url, payload in movements:
        response = client.post(url, json=payload, headers=headers)
        assert response.status_code == 201

    response = client.get(
        f"/api/productos/{product_id}/historial",
        headers=headers,
    )

    assert response.status_code == 200
    history = response.json()
    assert len(history) == 3
    assert [movement["tipo"] for movement in history] == [
        MOVEMENT_TYPE_ENTRADA,
        MOVEMENT_TYPE_ENTRADA,
        MOVEMENT_TYPE_SALIDA,
    ]
    assert history[0]["cantidad"] == 30
    assert history[1]["cantidad"] == 20
    assert history[2]["cantidad"] == 10
    assert history == sorted(history, key=lambda item: item["fecha"])
    for movement in history:
        assert movement["user_id"] is not None
        assert movement["fecha"]
        assert "stock_anterior" in movement
        assert "stock_nuevo" in movement


def test_pu_015_inmutabilidad_de_auditoria_servicio_y_http(
    client: TestClient,
    create_user: Callable[..., Any],
    auth_headers: Callable[[str, str], dict[str, str]],
    db_session: Session,
) -> None:
    admin_headers = _headers_for_role(
        create_user,
        auth_headers,
        role=ROLE_ADMINISTRADOR,
        email="admin-auditoria@eam.edu.co",
    )
    product_id = _create_product(client, admin_headers)
    movement_response = client.post(
        "/api/movimientos/entrada",
        json={"producto_id": product_id, "cantidad": 30},
        headers=admin_headers,
    )
    assert movement_response.status_code == 201
    movement_id = movement_response.json()["id"]

    with pytest.raises(OperacionNoPermitidaException):
        movement_service.actualizar_movimiento(
            db_session,
            movement_id,
            {"cantidad": 99},
        )

    db_session.expire_all()
    movement = db_session.get(Movement, movement_id)
    assert movement is not None
    assert movement.cantidad == 30

    put_response = client.put(
        f"/api/movimientos/{movement_id}",
        json={"cantidad": 99},
        headers=admin_headers,
    )
    delete_response = client.delete(
        f"/api/movimientos/{movement_id}",
        headers=admin_headers,
    )

    assert put_response.status_code == 403
    assert delete_response.status_code == 403

    history_response = client.get(
        f"/api/productos/{product_id}/historial",
        headers=admin_headers,
    )
    assert history_response.status_code == 200
    history = history_response.json()
    assert len(history) == 1
    assert history[0]["cantidad"] == 30
    assert history[0]["stock_anterior"] == 0
    assert history[0]["stock_nuevo"] == 30
