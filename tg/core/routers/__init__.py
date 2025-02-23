__all__ = ("router",)

from aiogram import Router
from tg.core.routers.messages import router as messages
from tg.core.routers.commands import router as commands

router = Router()
router.include_routers(
    commands,
    messages,
)
