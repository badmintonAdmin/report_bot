__all__ = ("router",)

from aiogram import Router
from .base import router as base

router = Router()
router.include_routers(
    base,
)
