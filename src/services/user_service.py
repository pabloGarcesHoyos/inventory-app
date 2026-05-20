from sqlalchemy.orm import Session

from src.exceptions.user_exceptions import (
    DuplicateEmailException,
    InactiveUserException,
    InvalidCredentialsException,
    InvalidRoleException,
    UserNotFoundException,
)
from src.models.user import ALLOWED_ROLES, STATUS_ACTIVO, STATUS_INACTIVO, User
from src.repositories import user_repository
from src.schemas.user import UserCreate
from src.security.password import get_password_hash, verify_password


def _ensure_valid_role(role: str) -> None:
    if role not in ALLOWED_ROLES:
        raise InvalidRoleException("Rol no valido")


def crear_usuario(db: Session, data: UserCreate) -> User:
    _ensure_valid_role(data.rol)
    if user_repository.exists_by_email(db, data.email):
        raise DuplicateEmailException("El email ya se encuentra registrado")

    user = User(
        nombre=data.nombre,
        email=data.email,
        hashed_password=get_password_hash(data.password),
        rol=data.rol,
        estado=STATUS_ACTIVO,
    )
    return user_repository.create(db, user)


def asignar_rol(db: Session, usuario_id: int, nuevo_rol: str) -> User:
    _ensure_valid_role(nuevo_rol)
    user = user_repository.get_by_id(db, usuario_id)
    if user is None:
        raise UserNotFoundException("Usuario no encontrado")

    user.rol = nuevo_rol
    return user_repository.update(db, user)


def eliminar_usuario(db: Session, usuario_id: int) -> User:
    user = user_repository.get_by_id(db, usuario_id)
    if user is None:
        raise UserNotFoundException("Usuario no encontrado")

    user.estado = STATUS_INACTIVO
    return user_repository.update(db, user)


def autenticar_usuario(db: Session, email: str, password: str) -> User:
    user = user_repository.get_by_email(db, email)
    if user is None or not verify_password(password, user.hashed_password):
        raise InvalidCredentialsException("Credenciales invalidas")

    if user.estado != STATUS_ACTIVO:
        raise InactiveUserException("Usuario inactivo")

    return user


def obtener_por_email(db: Session, email: str) -> User | None:
    return user_repository.get_by_email(db, email)


def obtener_por_id(db: Session, usuario_id: int) -> User | None:
    return user_repository.get_by_id(db, usuario_id)
