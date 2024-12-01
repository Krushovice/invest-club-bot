__all__ = ("router",)

from aiogram import Router

from .main_commands import router as main_commands_router


router = Router()
router.include_router(main_commands_router)
