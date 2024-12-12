__all__ = ("router",)

from aiogram import Router

from .commands.main_commands import router as main_commands_router
from .callback_handlers.pay_cb_handlers import router as pay_cb_router
from .channel_handlers.admin_handlers import router as channel_router


router = Router()
router.include_routers(
    main_commands_router,
    pay_cb_router,
    channel_router,
)
