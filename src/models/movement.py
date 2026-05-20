from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base

MOVEMENT_TYPE_ENTRADA = "ENTRADA"
MOVEMENT_TYPE_SALIDA = "SALIDA"
ALLOWED_MOVEMENT_TYPES = {MOVEMENT_TYPE_ENTRADA, MOVEMENT_TYPE_SALIDA}


def utc_now() -> datetime:
    return datetime.now(UTC)


class Movement(Base):
    __tablename__ = "movements"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    stock_anterior: Mapped[int] = mapped_column(Integer, nullable=False)
    stock_nuevo: Mapped[int] = mapped_column(Integer, nullable=False)
    documento: Mapped[str | None] = mapped_column(String(120), nullable=True)
    proveedor: Mapped[str | None] = mapped_column(String(150), nullable=True)
    destino: Mapped[str | None] = mapped_column(String(150), nullable=True)
    motivo: Mapped[str | None] = mapped_column(String(255), nullable=True)
    fecha: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    product = relationship("Product")
    user = relationship("User")

    @property
    def producto_id(self) -> int:
        return self.product_id
