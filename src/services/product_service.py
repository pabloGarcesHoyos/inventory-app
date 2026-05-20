from sqlalchemy.orm import Session

from src.exceptions.product_exceptions import (
    DuplicateSKUException,
    ProductNotFoundException,
)
from src.models.product import PRODUCT_STATUS_ACTIVO, Product
from src.repositories import product_repository
from src.schemas.product import ProductCreate, ProductUpdate


def registrar_producto(db: Session, data: ProductCreate) -> Product:
    if product_repository.exists_by_sku(db, data.sku):
        raise DuplicateSKUException("El SKU ya se encuentra registrado")

    product = Product(
        nombre=data.nombre,
        sku=data.sku,
        categoria=data.categoria,
        stock_actual=data.stock_inicial,
        stock_minimo=data.stock_minimo,
        unidad=data.unidad,
        estado=PRODUCT_STATUS_ACTIVO,
    )
    return product_repository.create(db, product)


def actualizar_producto(
    db: Session, producto_id: int, data: ProductUpdate
) -> Product:
    product = product_repository.get_by_id(db, producto_id)
    if product is None:
        raise ProductNotFoundException("Producto no encontrado")

    update_data = data.model_dump(exclude_unset=True)
    for field in ("nombre", "categoria", "stock_minimo", "unidad"):
        value = update_data.get(field)
        if value is not None:
            setattr(product, field, value)

    return product_repository.update(db, product)


def obtener_producto(db: Session, producto_id: int) -> Product:
    product = product_repository.get_by_id(db, producto_id)
    if product is None:
        raise ProductNotFoundException("Producto no encontrado")
    return product


def listar_productos(db: Session) -> list[Product]:
    return product_repository.list_all(db)
