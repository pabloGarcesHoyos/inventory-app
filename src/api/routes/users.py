from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.exceptions.user_exceptions import (
    DuplicateEmailException,
    InvalidRoleException,
    UserNotFoundException,
)
from src.models.user import User
from src.schemas.user import UserCreate, UserResponse, UserRoleUpdate
from src.security.dependencies import get_current_user, require_admin
from src.services.user_service import asignar_rol, crear_usuario, eliminar_usuario

router = APIRouter(prefix="/api/usuarios", tags=["usuarios"])


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
) -> User:
    try:
        return crear_usuario(db, data)
    except DuplicateEmailException as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except InvalidRoleException as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.put("/{usuario_id}/rol", response_model=UserResponse)
def update_user_role(
    usuario_id: int,
    data: UserRoleUpdate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin()),
) -> User:
    try:
        return asignar_rol(db, usuario_id, data.rol)
    except UserNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except InvalidRoleException as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.delete("/{usuario_id}", response_model=UserResponse)
def delete_user(
    usuario_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin()),
) -> User:
    try:
        return eliminar_usuario(db, usuario_id)
    except UserNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
