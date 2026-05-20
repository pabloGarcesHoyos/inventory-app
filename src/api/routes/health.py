from fastapi import APIRouter

from src.core.config import settings

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "inventory-api",
        "version": settings.APP_VERSION,
    }
