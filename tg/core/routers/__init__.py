__all__ = ("router",)

from aiogram import Router
from tg.core.routers.messages import router as msg_main

router = Router()
router.include_routers(
    msg_main,
)
