from src.api.routes.auth import router as auth_router
from src.api.routes.health import router as health_router
from src.api.routes.users import router as users_router

__all__ = ["auth_router", "health_router", "users_router"]
