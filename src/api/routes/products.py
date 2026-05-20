from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.exceptions.product_exceptions import (
    DuplicateSKUException,
    ProductNotFoundException,
    ProductValidationException,
)
from src.models.product import Product
from src.models.user import ROLE_ADMINISTRADOR, ROLE_OPERADOR, User
from src.schemas.product import ProductCreate, ProductResponse, ProductUpdate
from src.security.dependencies import (
    get_current_user,
    require_admin,
    require_any_role,
)
from src.services.product_service import (
    actualizar_producto,
    listar_productos,
    obtener_producto,
    registrar_producto,
)

router = APIRouter(prefix="/api/productos", tags=["productos"])


def _map_product_exception(exc: Exception) -> HTTPException:
    if isinstance(exc, DuplicateSKUException):
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )
    if isinstance(exc, ProductNotFoundException):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
    if isinstance(exc, ProductValidationException):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Error interno del servidor",
    )


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(
        require_any_role([ROLE_ADMINISTRADOR, ROLE_OPERADOR])
    ),
) -> Product:
    try:
        return registrar_producto(db, data)
    except (
        DuplicateSKUException,
        ProductValidationException,
    ) as exc:
        raise _map_product_exception(exc) from exc


@router.get("", response_model=list[ProductResponse])
def list_products(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> list[Product]:
    return listar_productos(db)


@router.get("/{producto_id}", response_model=ProductResponse)
def get_product(
    producto_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> Product:
    try:
        return obtener_producto(db, producto_id)
    except ProductNotFoundException as exc:
        raise _map_product_exception(exc) from exc


@router.put("/{producto_id}", response_model=ProductResponse)
def update_product(
    producto_id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin()),
) -> Product:
    try:
        return actualizar_producto(db, producto_id, data)
    except (
        ProductNotFoundException,
        ProductValidationException,
    ) as exc:
        raise _map_product_exception(exc) from exc
