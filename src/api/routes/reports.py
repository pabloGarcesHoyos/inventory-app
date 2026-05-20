from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.models.user import (
    ROLE_ADMINISTRADOR,
    ROLE_AUDITOR,
    ROLE_OPERADOR,
    User,
)
from src.schemas.report import InventoryReportResponse
from src.security.dependencies import require_any_role
from src.services.report_service import generar_reporte_inventario

router = APIRouter(prefix="/api/reportes", tags=["reportes"])


@router.get("/inventario", response_model=InventoryReportResponse)
def get_inventory_report(
    fecha_corte: str | None = None,
    db: Session = Depends(get_db),
    _current_user: User = Depends(
        require_any_role([ROLE_ADMINISTRADOR, ROLE_OPERADOR, ROLE_AUDITOR])
    ),
) -> InventoryReportResponse:
    return generar_reporte_inventario(db, fecha_corte=fecha_corte)
