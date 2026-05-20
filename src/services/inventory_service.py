from sqlalchemy.orm import Session

from src.exceptions.product_exceptions import ProductNotFoundException
from src.repositories import product_repository
from src.schemas.inventory import InventoryResponse


def consultar_existencias(db: Session, producto_id: int) -> InventoryResponse:
    product = product_repository.get_by_id(db, producto_id)
    if product is None:
        raise ProductNotFoundException("Producto no encontrado")

    estado_stock = (
        "OK" if product.stock_actual >= product.stock_minimo else "ALERTA"
    )
    return InventoryResponse(
        producto_id=product.id,
        nombre=product.nombre,
        sku=product.sku,
        stock_actual=product.stock_actual,
        stock_minimo=product.stock_minimo,
        unidad=product.unidad,
        estado_stock=estado_stock,
    )
