from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base

PRODUCT_STATUS_ACTIVO = "ACTIVO"
PRODUCT_STATUS_INACTIVO = "INACTIVO"
ALLOWED_PRODUCT_STATUSES = {PRODUCT_STATUS_ACTIVO, PRODUCT_STATUS_INACTIVO}


def utc_now() -> datetime:
    return datetime.now(UTC)


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    sku: Mapped[str] = mapped_column(
        String(80), unique=True, index=True, nullable=False
    )
    categoria: Mapped[str] = mapped_column(String(100), nullable=False)
    stock_actual: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    stock_minimo: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    unidad: Mapped[str] = mapped_column(
        String(50), nullable=False, default="unidades"
    )
    estado: Mapped[str] = mapped_column(
        String(20), nullable=False, default=PRODUCT_STATUS_ACTIVO
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=None, onupdate=utc_now, nullable=True
    )
