from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MovementEntryCreate(BaseModel):
    producto_id: int
    cantidad: int = Field(..., gt=0)
    proveedor: str | None = None
    documento: str | None = None
    fecha: datetime | None = None

    model_config = ConfigDict(extra="forbid")


class MovementExitCreate(BaseModel):
    producto_id: int
    cantidad: int = Field(..., gt=0)
    destino: str | None = None
    motivo: str | None = None
    fecha: datetime | None = None

    model_config = ConfigDict(extra="forbid")


class MovementResponse(BaseModel):
    id: int
    producto_id: int
    user_id: int
    tipo: str
    cantidad: int
    stock_anterior: int
    stock_nuevo: int
    documento: str | None
    proveedor: str | None
    destino: str | None
    motivo: str | None
    fecha: datetime

    model_config = ConfigDict(from_attributes=True)


HistoryResponse = MovementResponse
