from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.models.user import ROLE_ADMINISTRADOR, STATUS_ACTIVO, User
from src.security.jwt import decode_access_token
from src.services.user_service import obtener_por_email

bearer_scheme = HTTPBearer(auto_error=False)


def _unauthorized_exception(detail: str = "No autenticado") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise _unauthorized_exception()

    if credentials.scheme.lower() != "bearer":
        raise _unauthorized_exception("Token invalido")

    try:
        payload = decode_access_token(credentials.credentials)
    except JWTError as exc:
        raise _unauthorized_exception("Token invalido") from exc

    email = payload.get("sub")
    user_id = payload.get("user_id")
    if email is None or user_id is None:
        raise _unauthorized_exception("Token invalido")

    user = obtener_por_email(db, email)
    if user is None:
        raise _unauthorized_exception("Token invalido")

    try:
        token_user_id = int(user_id)
    except (TypeError, ValueError) as exc:
        raise _unauthorized_exception("Token invalido") from exc

    if user.id != token_user_id:
        raise _unauthorized_exception("Token invalido")

    if user.estado != STATUS_ACTIVO:
        raise _unauthorized_exception("Usuario inactivo")

    return user


def require_role(required_role: str) -> Callable[[User], User]:
    def role_dependency(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if current_user.rol != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos para ejecutar esta operacion",
            )
        return current_user

    return role_dependency


def require_admin() -> Callable[[User], User]:
    return require_role(ROLE_ADMINISTRADOR)
