from aiogram import Router, F
from aiogram.types import CallbackQuery

from aiogram.utils import markdown

from app.keyboards import PayCbData, PayActions

from app.routers.commands.main_commands import command_start_handler

from app.core.config import settings


router = Router(name=__name__)


@router.callback_query(PayCbData.filter(F.action == PayActions.back))
async def handle_back_button(call: CallbackQuery):
    await call.answer()
    await command_start_handler(message=call.message)


@router.callback_query(PayCbData.filter(F.action == PayActions.help))
async def handle_help_button(call: CallbackQuery):
    await call.answer()
    msg = (
        f"Если у вас возникли проблемы с оплатой, доступом к каналу, "
        f"вы можете описать суть проблемы мне на почту: {settings.main.admin_mail} и мы оперативно вам поможем👍"
    )

    await call.message.answer(
        text=markdown.text(markdown.hbold(msg)),
    )
