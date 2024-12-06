from aiogram import Bot
from aiogram.types import CallbackQuery

from app.core.config import settings


async def handle_new_member(call: CallbackQuery, name: str):
    msg = (
        f"Приветствую, {name}!"
        f"Добро пожаловать в узкий круг инвесторов🤝 "
        f"Здесь вы найдёте всю актуальную информацию по сделкам и стратегии следования ✍ "
    )

    # await call.message.new_chat_members(chat_id=settings.main.admin_id, text=msg)
