from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile

from aiogram.utils import markdown

from app.keyboards import PayCbData, PayActions, pay_kb

from app.routers.commands.main_commands import command_start_handler

from app.routers.channel_handlers import handle_new_member


router = Router(name=__name__)


@router.callback_query(PayCbData.filter(F.action == PayActions.back))
async def handle_back_button(call: CallbackQuery):
    await call.answer()
    await command_start_handler(message=call.message)
    await handle_new_member(call, name=call.message.from_user.first_name)
