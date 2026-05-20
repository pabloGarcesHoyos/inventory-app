from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base

ROLE_ADMINISTRADOR = "ADMINISTRADOR"
ROLE_OPERADOR = "OPERADOR"
ROLE_AUDITOR = "AUDITOR"
ALLOWED_ROLES = {ROLE_ADMINISTRADOR, ROLE_OPERADOR, ROLE_AUDITOR}

STATUS_ACTIVO = "ACTIVO"
STATUS_INACTIVO = "INACTIVO"
ALLOWED_STATUSES = {STATUS_ACTIVO, STATUS_INACTIVO}


def utc_now() -> datetime:
    return datetime.now(UTC)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(
        String(150), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    rol: Mapped[str] = mapped_column(
        String(30), nullable=False, default=ROLE_OPERADOR
    )
    estado: Mapped[str] = mapped_column(
        String(20), nullable=False, default=STATUS_ACTIVO
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=None, onupdate=utc_now, nullable=True
    )
