from sqlalchemy.orm import Session

from src.repositories import product_repository
from src.schemas.report import InventoryReportResponse, ReportProductItem


def generar_reporte_inventario(
    db: Session, fecha_corte: str | None = None
) -> InventoryReportResponse:
    products = product_repository.list_all(db)
    report_products = []
    total_en_alerta = 0

    for product in products:
        estado = "OK" if product.stock_actual >= product.stock_minimo else "ALERTA"
        if estado == "ALERTA":
            total_en_alerta += 1

        report_products.append(
            ReportProductItem(
                id=product.id,
                nombre=product.nombre,
                sku=product.sku,
                categoria=product.categoria,
                stock_actual=product.stock_actual,
                stock_minimo=product.stock_minimo,
                unidad=product.unidad,
                estado=estado,
            )
        )

    return InventoryReportResponse(
        formato="JSON",
        fecha_corte=fecha_corte,
        total_productos=len(report_products),
        total_en_alerta=total_en_alerta,
        productos=report_products,
    )
