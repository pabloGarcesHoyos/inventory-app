from pydantic import BaseModel, ConfigDict


class ReportProductItem(BaseModel):
    id: int
    nombre: str
    sku: str
    categoria: str
    stock_actual: int
    stock_minimo: int
    unidad: str
    estado: str

    model_config = ConfigDict(from_attributes=True)


class InventoryReportResponse(BaseModel):
    formato: str
    fecha_corte: str | None
    total_productos: int
    total_en_alerta: int
    productos: list[ReportProductItem]
