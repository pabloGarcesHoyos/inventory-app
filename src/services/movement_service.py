from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session

from src.exceptions.movement_exceptions import (
    CantidadInvalidaException,
    OperacionNoPermitidaException,
    StockInsuficienteException,
)
from src.exceptions.product_exceptions import ProductNotFoundException
from src.models.movement import MOVEMENT_TYPE_ENTRADA, MOVEMENT_TYPE_SALIDA, Movement
from src.models.user import User
from src.repositories import movement_repository, product_repository
from src.schemas.movement import MovementEntryCreate, MovementExitCreate
from src.services.alert_service import generar_alerta_stock_minimo


def _current_time() -> datetime:
    return datetime.now(UTC)


def _validate_cantidad(cantidad: int) -> None:
    if cantidad <= 0:
        raise CantidadInvalidaException("La cantidad debe ser mayor que cero")


def registrar_entrada(
    db: Session, data: MovementEntryCreate, current_user: User
) -> Movement:
    _validate_cantidad(data.cantidad)
    product = product_repository.get_by_id(db, data.producto_id)
    if product is None:
        raise ProductNotFoundException("Producto no encontrado")

    stock_anterior = product.stock_actual
    stock_nuevo = stock_anterior + data.cantidad
    product.stock_actual = stock_nuevo

    movement = Movement(
        product_id=product.id,
        user_id=current_user.id,
        tipo=MOVEMENT_TYPE_ENTRADA,
        cantidad=data.cantidad,
        stock_anterior=stock_anterior,
        stock_nuevo=stock_nuevo,
        documento=data.documento,
        proveedor=data.proveedor,
        fecha=data.fecha or _current_time(),
    )
    return movement_repository.create(db, movement)


def registrar_salida(
    db: Session, data: MovementExitCreate, current_user: User
) -> Movement:
    _validate_cantidad(data.cantidad)
    product = product_repository.get_by_id(db, data.producto_id)
    if product is None:
        raise ProductNotFoundException("Producto no encontrado")

    stock_anterior = product.stock_actual
    if data.cantidad > stock_anterior:
        raise StockInsuficienteException("Stock insuficiente para la salida")

    stock_nuevo = stock_anterior - data.cantidad
    product.stock_actual = stock_nuevo

    movement = Movement(
        product_id=product.id,
        user_id=current_user.id,
        tipo=MOVEMENT_TYPE_SALIDA,
        cantidad=data.cantidad,
        stock_anterior=stock_anterior,
        stock_nuevo=stock_nuevo,
        destino=data.destino,
        motivo=data.motivo,
        fecha=data.fecha or _current_time(),
    )
    movement = movement_repository.create(db, movement)

    if stock_nuevo < product.stock_minimo:
        generar_alerta_stock_minimo(db, product)

    return movement


def obtener_historial_producto(
    db: Session,
    producto_id: int,
    fecha_inicio: datetime | None = None,
    fecha_fin: datetime | None = None,
) -> list[Movement]:
    product = product_repository.get_by_id(db, producto_id)
    if product is None:
        raise ProductNotFoundException("Producto no encontrado")
    return movement_repository.list_by_product(
        db,
        producto_id,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
    )


def actualizar_movimiento(
    db: Session, movimiento_id: int, data: dict[str, Any] | None = None
) -> None:
    _ = db, movimiento_id, data
    raise OperacionNoPermitidaException(
        "Los movimientos de inventario no pueden modificarse"
    )


def eliminar_movimiento(db: Session, movimiento_id: int) -> None:
    _ = db, movimiento_id
    raise OperacionNoPermitidaException(
        "Los movimientos de inventario no pueden eliminarse"
    )
