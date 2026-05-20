from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.routes import auth_router, health_router, users_router
from src.core.config import settings
from src.core.database import init_db


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    init_db()
    yield

app = FastAPI(
    title=settings.APP_NAME,
    description="API REST para control y trazabilidad de inventarios",
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(users_router)


@app.get("/")
def read_root() -> dict[str, str]:
    return {
        "message": "API del Sistema de Gestión de Inventarios funcionando correctamente"
    }
