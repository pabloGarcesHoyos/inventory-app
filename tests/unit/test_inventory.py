from collections.abc import Callable
from typing import Any

from fastapi.testclient import TestClient

from src.models.user import ROLE_OPERADOR


def _headers_for_operator(
    create_user: Callable[..., Any],
    auth_headers: Callable[[str, str], dict[str, str]],
) -> dict[str, str]:
    response = create_user(
        nombre="Operador Inventario",
        email="operador-inventario@eam.edu.co",
        rol=ROLE_OPERADOR,
    )
    assert response.status_code == 201
    return auth_headers("operador-inventario@eam.edu.co")


def _create_product(client: TestClient, headers: dict[str, str]) -> int:
    response = client.post(
        "/api/productos",
        json={
            "nombre": "Resma de Papel",
            "sku": "PAP-INV-001",
            "categoria": "INSUMOS",
            "stock_inicial": 60,
            "stock_minimo": 10,
            "unidad": "unidades",
        },
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_pu_009_consulta_de_existencias_en_tiempo_real(
    client: TestClient,
    create_user: Callable[..., Any],
    auth_headers: Callable[[str, str], dict[str, str]],
) -> None:
    headers = _headers_for_operator(create_user, auth_headers)
    product_id = _create_product(client, headers)

    response = client.get(f"/api/inventario/{product_id}", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["producto_id"] == product_id
    assert data["nombre"] == "Resma de Papel"
    assert data["stock_actual"] == 60
    assert data["unidad"] == "unidades"
    assert data["estado_stock"] == "OK"


def test_consulta_inventario_requiere_token(client: TestClient) -> None:
    response = client.get("/api/inventario/1")

    assert response.status_code == 401
