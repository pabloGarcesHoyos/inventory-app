from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.exceptions.product_exceptions import ProductNotFoundException
from src.models.alert import Alert
from src.models.user import User
from src.schemas.alert import AlertResponse
from src.schemas.inventory import InventoryResponse
from src.security.dependencies import get_current_user
from src.services.alert_service import obtener_alertas_producto
from src.services.inventory_service import consultar_existencias

router = APIRouter(tags=["inventario"])


def _product_not_found_response(exc: ProductNotFoundException) -> HTTPException:
    return HTTPException(status_code=404, detail=str(exc))


@router.get("/api/inventario/{producto_id}", response_model=InventoryResponse)
def get_inventory(
    producto_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> InventoryResponse:
    try:
        return consultar_existencias(db, producto_id)
    except ProductNotFoundException as exc:
        raise _product_not_found_response(exc) from exc


@router.get(
    "/api/productos/{producto_id}/alertas",
    response_model=list[AlertResponse],
)
def get_product_alerts(
    producto_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> list[Alert]:
    try:
        return obtener_alertas_producto(db, producto_id)
    except ProductNotFoundException as exc:
        raise _product_not_found_response(exc) from exc
