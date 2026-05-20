from collections.abc import Callable
from typing import Any

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.models.movement import Movement
from src.models.product import Product
from src.models.user import ROLE_AUDITOR, ROLE_OPERADOR


def _headers_for_role(
    create_user: Callable[..., Any],
    auth_headers: Callable[[str, str], dict[str, str]],
    *,
    role: str = ROLE_OPERADOR,
    email: str = "usuario-reportes@eam.edu.co",
) -> dict[str, str]:
    response = create_user(
        nombre="Usuario Reportes",
        email=email,
        rol=role,
    )
    assert response.status_code == 201
    return auth_headers(email)


def _create_product(
    client: TestClient,
    headers: dict[str, str],
    *,
    index: int,
    stock_inicial: int,
    stock_minimo: int,
) -> dict[str, Any]:
    response = client.post(
        "/api/productos",
        json={
            "nombre": f"Producto {index}",
            "sku": f"REP-{index:03d}",
            "categoria": "INSUMOS",
            "stock_inicial": stock_inicial,
            "stock_minimo": stock_minimo,
            "unidad": "unidades",
        },
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


def test_pu_012_generacion_de_reporte_de_inventario_json(
    client: TestClient,
    create_user: Callable[..., Any],
    auth_headers: Callable[[str, str], dict[str, str]],
) -> None:
    headers = _headers_for_role(create_user, auth_headers)
    products_seed = [
        (60, 10),
        (5, 10),
        (12, 12),
        (0, 3),
        (20, 5),
    ]
    for index, (stock_inicial, stock_minimo) in enumerate(products_seed, start=1):
        _create_product(
            client,
            headers,
            index=index,
            stock_inicial=stock_inicial,
            stock_minimo=stock_minimo,
        )

    response = client.get(
        "/api/reportes/inventario?fecha_corte=2026-04-25",
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["formato"] == "JSON"
    assert data["fecha_corte"] == "2026-04-25"
    assert data["total_productos"] == 5
    assert data["total_en_alerta"] == 2
    assert len(data["productos"]) == 5

    for product in data["productos"]:
        assert product["nombre"]
        assert product["sku"]
        assert "stock_actual" in product
        assert "stock_minimo" in product
        assert product["estado"] in {"OK", "ALERTA"}
        expected_status = (
            "OK"
            if product["stock_actual"] >= product["stock_minimo"]
            else "ALERTA"
        )
        assert product["estado"] == expected_status


def test_reporte_inventario_requiere_token(client: TestClient) -> None:
    response = client.get("/api/reportes/inventario")

    assert response.status_code == 401


def test_reporte_inventario_sin_productos_responde_lista_vacia(
    client: TestClient,
    create_user: Callable[..., Any],
    auth_headers: Callable[[str, str], dict[str, str]],
) -> None:
    headers = _headers_for_role(create_user, auth_headers)

    response = client.get("/api/reportes/inventario", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["formato"] == "JSON"
    assert data["total_productos"] == 0
    assert data["total_en_alerta"] == 0
    assert data["productos"] == []


def test_auditor_puede_consultar_reporte(
    client: TestClient,
    create_user: Callable[..., Any],
    auth_headers: Callable[[str, str], dict[str, str]],
) -> None:
    auditor_headers = _headers_for_role(
        create_user,
        auth_headers,
        role=ROLE_AUDITOR,
        email="auditor-reportes@eam.edu.co",
    )

    response = client.get("/api/reportes/inventario", headers=auditor_headers)

    assert response.status_code == 200


def test_reporte_no_modifica_stock_ni_movimientos(
    client: TestClient,
    create_user: Callable[..., Any],
    auth_headers: Callable[[str, str], dict[str, str]],
    db_session: Session,
) -> None:
    headers = _headers_for_role(create_user, auth_headers)
    product = _create_product(
        client,
        headers,
        index=1,
        stock_inicial=25,
        stock_minimo=5,
    )
    product_id = product["id"]

    response = client.get("/api/reportes/inventario", headers=headers)

    assert response.status_code == 200
    db_session.expire_all()
    persisted_product = db_session.get(Product, product_id)
    assert persisted_product is not None
    assert persisted_product.stock_actual == 25
    assert db_session.query(Movement).count() == 0
