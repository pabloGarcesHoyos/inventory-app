from collections.abc import Callable
from typing import Any

from fastapi.testclient import TestClient

from src.models.alert import ALERT_TYPE_STOCK_MINIMO
from src.models.user import ROLE_OPERADOR


def _headers_for_operator(
    create_user: Callable[..., Any],
    auth_headers: Callable[[str, str], dict[str, str]],
) -> dict[str, str]:
    response = create_user(
        nombre="Operador Alertas",
        email="operador-alertas@eam.edu.co",
        rol=ROLE_OPERADOR,
    )
    assert response.status_code == 201
    return auth_headers("operador-alertas@eam.edu.co")


def test_pu_010_activacion_de_alerta_por_stock_minimo(
    client: TestClient,
    create_user: Callable[..., Any],
    auth_headers: Callable[[str, str], dict[str, str]],
) -> None:
    headers = _headers_for_operator(create_user, auth_headers)
    product_response = client.post(
        "/api/productos",
        json={
            "nombre": "Resma de Papel",
            "sku": "PAP-ALERTA-001",
            "categoria": "INSUMOS",
            "stock_inicial": 12,
            "stock_minimo": 10,
            "unidad": "unidades",
        },
        headers=headers,
    )
    assert product_response.status_code == 201
    product_id = product_response.json()["id"]

    movement_response = client.post(
        "/api/movimientos/salida",
        json={
            "producto_id": product_id,
            "cantidad": 5,
            "destino": "Departamento de Sistemas",
            "motivo": "Consumo interno",
        },
        headers=headers,
    )
    assert movement_response.status_code == 201
    assert movement_response.json()["stock_nuevo"] == 7

    response = client.get(f"/api/productos/{product_id}/alertas", headers=headers)

    assert response.status_code == 200
    alerts = response.json()
    assert len(alerts) >= 1
    assert alerts[0]["tipo"] == ALERT_TYPE_STOCK_MINIMO
    assert alerts[0]["stock_actual"] == 7
    assert alerts[0]["stock_minimo"] == 10
