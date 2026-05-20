from pydantic import BaseModel


class InventoryResponse(BaseModel):
    producto_id: int
    nombre: str
    sku: str
    stock_actual: int
    stock_minimo: int
    unidad: str
    estado_stock: str
