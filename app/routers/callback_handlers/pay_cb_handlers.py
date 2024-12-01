from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile

from aiogram.utils import markdown

from app.keyboards import PayCbData, PayActions, pay_kb

from routers.commands.main_commands import command_start_handler


router = Router(name=__name__)


@router.callback_query(PayCbData.filter(F.action == PayActions.back))
async def handle_back_button(call: CallbackQuery):
    await call.answer()
    await command_start_handler(message=call.message)
