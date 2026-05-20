from sqlalchemy.orm import Session

from src.exceptions.product_exceptions import ProductNotFoundException
from src.models.alert import ALERT_TYPE_STOCK_MINIMO, Alert
from src.models.product import Product
from src.repositories import alert_repository, product_repository


def generar_alerta_stock_minimo(db: Session, producto: Product) -> Alert:
    alert = Alert(
        product_id=producto.id,
        tipo=ALERT_TYPE_STOCK_MINIMO,
        mensaje=(
            f"El producto {producto.nombre} está por debajo del stock mínimo."
        ),
        stock_actual=producto.stock_actual,
        stock_minimo=producto.stock_minimo,
    )
    return alert_repository.create(db, alert)


def obtener_alertas_producto(db: Session, producto_id: int) -> list[Alert]:
    product = product_repository.get_by_id(db, producto_id)
    if product is None:
        raise ProductNotFoundException("Producto no encontrado")
    return alert_repository.list_by_product(db, producto_id)
