import re

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.models.user import ALLOWED_ROLES, ROLE_OPERADOR

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def normalize_email(value: str) -> str:
    email = value.strip().lower()
    if not EMAIL_PATTERN.match(email):
        raise ValueError("El email no tiene un formato valido")
    return email


def validate_role(value: str) -> str:
    role = value.strip().upper()
    if role not in ALLOWED_ROLES:
        raise ValueError("El rol no es valido")
    return role


class UserCreate(BaseModel):
    nombre: str = Field(..., min_length=1)
    email: str
    password: str = Field(..., min_length=6)
    rol: str = ROLE_OPERADOR

    @field_validator("nombre")
    @classmethod
    def validate_nombre(cls, value: str) -> str:
        nombre = value.strip()
        if not nombre:
            raise ValueError("El nombre no puede estar vacio")
        return nombre

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return normalize_email(value)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("La contrasena no puede estar vacia")
        return value

    @field_validator("rol")
    @classmethod
    def validate_user_role(cls, value: str) -> str:
        return validate_role(value)


class UserResponse(BaseModel):
    id: int
    nombre: str
    email: str
    rol: str
    estado: str

    model_config = ConfigDict(from_attributes=True)


class UserRoleUpdate(BaseModel):
    rol: str

    @field_validator("rol")
    @classmethod
    def validate_user_role(cls, value: str) -> str:
        return validate_role(value)
