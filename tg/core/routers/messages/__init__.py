__all__ = ("router",)

from aiogram import Router
from .main import router as msg_router

router = Router()
router.include_routers(
    msg_router,
)
