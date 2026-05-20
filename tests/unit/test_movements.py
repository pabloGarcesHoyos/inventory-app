from collections.abc import Callable
from typing import Any

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.models.movement import MOVEMENT_TYPE_ENTRADA, MOVEMENT_TYPE_SALIDA, Movement
from src.models.product import Product
from src.models.user import ROLE_OPERADOR


def _headers_for_operator(
    create_user: Callable[..., Any],
    auth_headers: Callable[[str, str], dict[str, str]],
    email: str = "operador-movimientos@eam.edu.co",
) -> dict[str, str]:
    response = create_user(
        nombre="Operador Movimientos",
        email=email,
        rol=ROLE_OPERADOR,
    )
    assert response.status_code == 201
    return auth_headers(email)


def _create_product(
    client: TestClient,
    headers: dict[str, str],
    *,
    sku: str = "PAP-001",
    stock_inicial: int = 50,
    stock_minimo: int = 10,
) -> int:
    response = client.post(
        "/api/productos",
        json={
            "nombre": "Resma de Papel",
            "sku": sku,
            "categoria": "INSUMOS",
            "stock_inicial": stock_inicial,
            "stock_minimo": stock_minimo,
            "unidad": "unidades",
        },
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_pu_006_registro_de_entrada_de_inventario(
    client: TestClient,
    create_user: Callable[..., Any],
    auth_headers: Callable[[str, str], dict[str, str]],
) -> None:
    headers = _headers_for_operator(create_user, auth_headers)
    product_id = _create_product(client, headers, stock_inicial=50)

    response = client.post(
        "/api/movimientos/entrada",
        json={
            "producto_id": product_id,
            "cantidad": 30,
            "proveedor": "Papelería Nacional",
            "documento": "FAC-2026-001",
        },
        headers=headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["tipo"] == MOVEMENT_TYPE_ENTRADA
    assert data["stock_anterior"] == 50
    assert data["stock_nuevo"] == 80

    inventory_response = client.get(
        f"/api/inventario/{product_id}",
        headers=headers,
    )
    assert inventory_response.status_code == 200
    assert inventory_response.json()["stock_actual"] == 80


def test_pu_007_registro_de_salida_de_inventario(
    client: TestClient,
    create_user: Callable[..., Any],
    auth_headers: Callable[[str, str], dict[str, str]],
) -> None:
    headers = _headers_for_operator(create_user, auth_headers)
    product_id = _create_product(client, headers, stock_inicial=80)

    response = client.post(
        "/api/movimientos/salida",
        json={
            "producto_id": product_id,
            "cantidad": 20,
            "destino": "Departamento de Sistemas",
            "motivo": "Consumo interno",
        },
        headers=headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["tipo"] == MOVEMENT_TYPE_SALIDA
    assert data["stock_anterior"] == 80
    assert data["stock_nuevo"] == 60

    inventory_response = client.get(
        f"/api/inventario/{product_id}",
        headers=headers,
    )
    assert inventory_response.status_code == 200
    assert inventory_response.json()["stock_actual"] == 60


def test_pu_008_rechazo_de_salida_por_stock_insuficiente(
    client: TestClient,
    create_user: Callable[..., Any],
    auth_headers: Callable[[str, str], dict[str, str]],
    db_session: Session,
) -> None:
    headers = _headers_for_operator(create_user, auth_headers)
    product_id = _create_product(client, headers, stock_inicial=10)

    response = client.post(
        "/api/movimientos/salida",
        json={
            "producto_id": product_id,
            "cantidad": 50,
            "destino": "Departamento de Sistemas",
            "motivo": "Consumo interno",
        },
        headers=headers,
    )

    assert response.status_code == 400
    assert "stock insuficiente" in response.json()["detail"].lower()

    inventory_response = client.get(
        f"/api/inventario/{product_id}",
        headers=headers,
    )
    assert inventory_response.status_code == 200
    assert inventory_response.json()["stock_actual"] == 10

    invalid_movements_count = (
        db_session.query(Movement)
        .filter(
            Movement.product_id == product_id,
            Movement.tipo == MOVEMENT_TYPE_SALIDA,
        )
        .count()
    )
    assert invalid_movements_count == 0


def test_entrada_requiere_token(client: TestClient) -> None:
    response = client.post(
        "/api/movimientos/entrada",
        json={"producto_id": 1, "cantidad": 1},
    )

    assert response.status_code == 401


def test_salida_requiere_token(client: TestClient) -> None:
    response = client.post(
        "/api/movimientos/salida",
        json={"producto_id": 1, "cantidad": 1},
    )

    assert response.status_code == 401


def test_cantidad_cero_en_entrada_responde_422(
    client: TestClient,
    create_user: Callable[..., Any],
    auth_headers: Callable[[str, str], dict[str, str]],
) -> None:
    headers = _headers_for_operator(create_user, auth_headers)

    response = client.post(
        "/api/movimientos/entrada",
        json={"producto_id": 1, "cantidad": 0},
        headers=headers,
    )

    assert response.status_code == 422


def test_producto_inexistente_en_movimiento_responde_404(
    client: TestClient,
    create_user: Callable[..., Any],
    auth_headers: Callable[[str, str], dict[str, str]],
) -> None:
    headers = _headers_for_operator(create_user, auth_headers)

    response = client.post(
        "/api/movimientos/entrada",
        json={"producto_id": 999, "cantidad": 5},
        headers=headers,
    )

    assert response.status_code == 404


def test_salida_fallida_no_modifica_stock_del_producto(
    client: TestClient,
    create_user: Callable[..., Any],
    auth_headers: Callable[[str, str], dict[str, str]],
    db_session: Session,
) -> None:
    headers = _headers_for_operator(create_user, auth_headers)
    product_id = _create_product(client, headers, stock_inicial=10)

    response = client.post(
        "/api/movimientos/salida",
        json={"producto_id": product_id, "cantidad": 99},
        headers=headers,
    )

    assert response.status_code == 400
    db_session.expire_all()
    product = db_session.get(Product, product_id)
    assert product is not None
    assert product.stock_actual == 10
