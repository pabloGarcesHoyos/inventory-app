from src.api.routes.auth import router as auth_router
from src.api.routes.health import router as health_router
from src.api.routes.inventory import router as inventory_router
from src.api.routes.movements import router as movements_router
from src.api.routes.products import router as products_router
from src.api.routes.reports import router as reports_router
from src.api.routes.users import router as users_router

__all__ = [
    "auth_router",
    "health_router",
    "inventory_router",
    "movements_router",
    "products_router",
    "reports_router",
    "users_router",
]
