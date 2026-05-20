from fastapi import FastAPI

from src.api.routes.health import router as health_router
from src.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description="API REST para control y trazabilidad de inventarios",
    version=settings.APP_VERSION,
)

app.include_router(health_router)


@app.get("/")
def read_root() -> dict[str, str]:
    return {
        "message": "API del Sistema de Gestión de Inventarios funcionando correctamente"
    }
