from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AlertResponse(BaseModel):
    id: int
    producto_id: int
    tipo: str
    mensaje: str
    stock_actual: int
    stock_minimo: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
