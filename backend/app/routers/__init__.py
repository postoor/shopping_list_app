from .auth import router as auth_router
from .friends import router as friends_router
from .items import router as items_router
from .groups import router as groups_router
from .plans import router as plans_router

__all__ = [
    "auth_router", "friends_router", "items_router",
    "groups_router", "plans_router",
]
