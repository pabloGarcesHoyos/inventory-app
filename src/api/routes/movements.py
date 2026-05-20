from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.exceptions.movement_exceptions import (
    CantidadInvalidaException,
    MovimientoNoEncontradoException,
    OperacionNoPermitidaException,
    StockInsuficienteException,
)
from src.exceptions.product_exceptions import ProductNotFoundException
from src.models.movement import Movement
from src.models.user import ROLE_ADMINISTRADOR, ROLE_OPERADOR, User
from src.schemas.movement import (
    HistoryResponse,
    MovementEntryCreate,
    MovementExitCreate,
    MovementResponse,
)
from src.security.dependencies import get_current_user, require_admin, require_any_role
from src.services.movement_service import (
    actualizar_movimiento,
    eliminar_movimiento,
    obtener_historial_producto,
    registrar_entrada,
    registrar_salida,
)

router = APIRouter(tags=["movimientos"])


def _map_movement_exception(exc: Exception) -> HTTPException:
    if isinstance(exc, StockInsuficienteException):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    if isinstance(exc, CantidadInvalidaException):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    if isinstance(exc, MovimientoNoEncontradoException):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
    if isinstance(exc, ProductNotFoundException):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
    if isinstance(exc, OperacionNoPermitidaException):
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Error interno del servidor",
    )


@router.post(
    "/api/movimientos/entrada",
    response_model=MovementResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_entry_movement(
    data: MovementEntryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_any_role([ROLE_ADMINISTRADOR, ROLE_OPERADOR])
    ),
) -> Movement:
    try:
        return registrar_entrada(db, data, current_user)
    except (
        CantidadInvalidaException,
        ProductNotFoundException,
    ) as exc:
        raise _map_movement_exception(exc) from exc


@router.post(
    "/api/movimientos/salida",
    response_model=MovementResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_exit_movement(
    data: MovementExitCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_any_role([ROLE_ADMINISTRADOR, ROLE_OPERADOR])
    ),
) -> Movement:
    try:
        return registrar_salida(db, data, current_user)
    except (
        CantidadInvalidaException,
        ProductNotFoundException,
        StockInsuficienteException,
    ) as exc:
        raise _map_movement_exception(exc) from exc


@router.get(
    "/api/productos/{producto_id}/historial",
    response_model=list[HistoryResponse],
)
def get_product_history(
    producto_id: int,
    fecha_inicio: datetime | None = None,
    fecha_fin: datetime | None = None,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> list[Movement]:
    try:
        return obtener_historial_producto(
            db,
            producto_id,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
        )
    except ProductNotFoundException as exc:
        raise _map_movement_exception(exc) from exc


@router.put("/api/movimientos/{movimiento_id}")
def update_movement(
    movimiento_id: int,
    data: dict[str, Any],
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin()),
) -> None:
    try:
        actualizar_movimiento(db, movimiento_id, data)
    except OperacionNoPermitidaException as exc:
        raise _map_movement_exception(exc) from exc


@router.delete("/api/movimientos/{movimiento_id}")
def delete_movement(
    movimiento_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin()),
) -> None:
    try:
        eliminar_movimiento(db, movimiento_id)
    except OperacionNoPermitidaException as exc:
        raise _map_movement_exception(exc) from exc
