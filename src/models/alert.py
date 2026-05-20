from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base

ALERT_TYPE_STOCK_MINIMO = "STOCK_MINIMO"
ALLOWED_ALERT_TYPES = {ALERT_TYPE_STOCK_MINIMO}


def utc_now() -> datetime:
    return datetime.now(UTC)


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"), nullable=False, index=True
    )
    tipo: Mapped[str] = mapped_column(String(30), nullable=False)
    mensaje: Mapped[str] = mapped_column(String(255), nullable=False)
    stock_actual: Mapped[int] = mapped_column(Integer, nullable=False)
    stock_minimo: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    product = relationship("Product")

    @property
    def producto_id(self) -> int:
        return self.product_id
