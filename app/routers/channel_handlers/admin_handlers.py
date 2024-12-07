from aiogram import Bot, Router, F
from aiogram.types import CallbackQuery

from app.core.config import settings

# from app.core.models import User

from app.keyboards.chat_kb import ChatCbData, ChatActions, build_chat_kb

router = Router(name=__name__)


@router.callback_query(ChatCbData.filter(F.action == ChatActions.join))
async def handle_new_member(call: CallbackQuery, bot: Bot):
    msg = (
        f"Приветствую!"
        f"Добро пожаловать в узкий круг инвесторов🤝 "
        f"Здесь вы найдёте всю актуальную информацию по сделкам и стратегии следования ✍ "
    )

    # if user.subscription:
    await bot.approve_chat_join_request(
        chat_id=int(settings.main.channel_id),
        user_id=1130398207,
    )
    await call.message.answer(msg)
