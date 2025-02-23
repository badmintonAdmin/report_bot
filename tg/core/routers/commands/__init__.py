__all__ = ("router",)

from aiogram import Router
from .base import router as base
from .reports import router as reports
from .search import router as search

router = Router()
router.include_routers(
    search,
    reports,
    base,
)
