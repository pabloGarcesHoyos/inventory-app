from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.exceptions.user_exceptions import (
    InactiveUserException,
    InvalidCredentialsException,
)
from src.schemas.auth import LoginRequest, TokenResponse
from src.security.jwt import create_access_token
from src.services.user_service import autenticar_usuario

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    try:
        user = autenticar_usuario(db, data.email, data.password)
    except (InvalidCredentialsException, InactiveUserException) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    access_token = create_access_token(
        data={
            "sub": user.email,
            "role": user.rol,
            "user_id": user.id,
        }
    )
    return TokenResponse(access_token=access_token)
