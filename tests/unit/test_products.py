from collections.abc import Callable
from typing import Any

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.models.product import PRODUCT_STATUS_ACTIVO, Product
from src.models.user import ROLE_ADMINISTRADOR, ROLE_OPERADOR


def _product_payload(
    *,
    nombre: str = "Resma de Papel",
    sku: str | None = "PAP-001",
    categoria: str = "INSUMOS",
    stock_inicial: int = 50,
    stock_minimo: int = 10,
    unidad: str = "unidades",
) -> dict[str, Any]:
    return {
        "nombre": nombre,
        "sku": sku,
        "categoria": categoria,
        "stock_inicial": stock_inicial,
        "stock_minimo": stock_minimo,
        "unidad": unidad,
    }


def _create_operator_and_headers(
    create_user: Callable[..., Any],
    auth_headers: Callable[[str, str], dict[str, str]],
    email: str = "operador-productos@eam.edu.co",
) -> dict[str, str]:
    response = create_user(
        nombre="Operador Productos",
        email=email,
        rol=ROLE_OPERADOR,
    )
    assert response.status_code == 201
    return auth_headers(email)


def _create_admin_and_headers(
    create_user: Callable[..., Any],
    auth_headers: Callable[[str, str], dict[str, str]],
    email: str = "admin-productos@eam.edu.co",
) -> dict[str, str]:
    response = create_user(
        nombre="Admin Productos",
        email=email,
        rol=ROLE_ADMINISTRADOR,
    )
    assert response.status_code == 201
    return auth_headers(email)


def test_pu_004_registro_de_producto_con_datos_validos(
    client: TestClient,
    create_user: Callable[..., Any],
    auth_headers: Callable[[str, str], dict[str, str]],
) -> None:
    headers = _create_operator_and_headers(create_user, auth_headers)

    response = client.post(
        "/api/productos",
        json=_product_payload(),
        headers=headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["sku"] == "PAP-001"
    assert data["stock_actual"] == 50
    assert data["estado"] == PRODUCT_STATUS_ACTIVO


def test_pu_005_rechaza_producto_con_sku_duplicado(
    client: TestClient,
    create_user: Callable[..., Any],
    auth_headers: Callable[[str, str], dict[str, str]],
    db_session: Session,
) -> None:
    headers = _create_operator_and_headers(create_user, auth_headers)

    first_response = client.post(
        "/api/productos",
        json=_product_payload(),
        headers=headers,
    )
    second_response = client.post(
        "/api/productos",
        json=_product_payload(nombre="Resma Carta"),
        headers=headers,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    products_count = (
        db_session.query(Product).filter(Product.sku == "PAP-001").count()
    )
    assert products_count == 1


def test_pu_016_modificacion_de_datos_de_producto_existente(
    client: TestClient,
    create_user: Callable[..., Any],
    auth_headers: Callable[[str, str], dict[str, str]],
) -> None:
    headers = _create_admin_and_headers(create_user, auth_headers)
    create_response = client.post(
        "/api/productos",
        json=_product_payload(),
        headers=headers,
    )
    product_id = create_response.json()["id"]

    response = client.put(
        f"/api/productos/{product_id}",
        json={
            "nombre": "Resma de Papel A4",
            "categoria": "PAPELERÍA",
            "stock_minimo": 15,
            "unidad": "unidades",
        },
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["nombre"] == "Resma de Papel A4"
    assert data["categoria"] == "PAPELERÍA"
    assert data["stock_minimo"] == 15
    assert data["sku"] == "PAP-001"
    assert data["stock_actual"] == 50


def test_pu_018_validacion_de_campos_obligatorios_en_producto(
    client: TestClient,
    create_user: Callable[..., Any],
    auth_headers: Callable[[str, str], dict[str, str]],
) -> None:
    headers = _create_operator_and_headers(create_user, auth_headers)

    response = client.post(
        "/api/productos",
        json=_product_payload(nombre="", sku=None),
        headers=headers,
    )

    assert response.status_code == 422
    response_text = response.text
    assert "nombre" in response_text
    assert "sku" in response_text


def test_get_productos_requiere_token(client: TestClient) -> None:
    response = client.get("/api/productos")

    assert response.status_code == 401


def test_get_productos_con_token_valido_responde_200(
    client: TestClient,
    create_user: Callable[..., Any],
    auth_headers: Callable[[str, str], dict[str, str]],
) -> None:
    headers = _create_operator_and_headers(create_user, auth_headers)

    response = client.get("/api/productos", headers=headers)

    assert response.status_code == 200
    assert response.json() == []


def test_get_producto_por_id_con_token_valido_responde_200(
    client: TestClient,
    create_user: Callable[..., Any],
    auth_headers: Callable[[str, str], dict[str, str]],
) -> None:
    headers = _create_operator_and_headers(create_user, auth_headers)
    create_response = client.post(
        "/api/productos",
        json=_product_payload(),
        headers=headers,
    )
    product_id = create_response.json()["id"]

    response = client.get(f"/api/productos/{product_id}", headers=headers)

    assert response.status_code == 200
    assert response.json()["sku"] == "PAP-001"


def test_operador_no_puede_modificar_producto(
    client: TestClient,
    create_user: Callable[..., Any],
    auth_headers: Callable[[str, str], dict[str, str]],
    db_session: Session,
) -> None:
    headers = _create_operator_and_headers(create_user, auth_headers)
    create_response = client.post(
        "/api/productos",
        json=_product_payload(),
        headers=headers,
    )
    product_id = create_response.json()["id"]

    response = client.put(
        f"/api/productos/{product_id}",
        json={"nombre": "Producto no permitido"},
        headers=headers,
    )

    assert response.status_code == 403
    db_session.expire_all()
    product = db_session.get(Product, product_id)
    assert product is not None
    assert product.nombre == "Resma de Papel"


def test_update_producto_no_permite_modificar_sku(
    client: TestClient,
    create_user: Callable[..., Any],
    auth_headers: Callable[[str, str], dict[str, str]],
    db_session: Session,
) -> None:
    headers = _create_admin_and_headers(create_user, auth_headers)
    create_response = client.post(
        "/api/productos",
        json=_product_payload(),
        headers=headers,
    )
    product_id = create_response.json()["id"]

    response = client.put(
        f"/api/productos/{product_id}",
        json={"sku": "PAP-999", "nombre": "Resma A4"},
        headers=headers,
    )

    assert response.status_code == 422
    db_session.expire_all()
    product = db_session.get(Product, product_id)
    assert product is not None
    assert product.sku == "PAP-001"
