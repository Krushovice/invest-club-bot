import logging

from aiogram import Router, F
from aiogram.types import CallbackQuery, ChatMemberUpdated, ChatJoinRequest

from aiogram.exceptions import TelegramBadRequest
from sqlalchemy.exc import SQLAlchemyError

from app.keyboards.chat_kb import ChatCbData, ChatActions
from app.core.config import settings

from app.core.database import UserCRUD

router = Router(name=__name__)


@router.callback_query(ChatCbData.filter(F.action == ChatActions.join))
async def handle_new_member(call: CallbackQuery):
    await call.answer()


@router.chat_join_request(F.chat.id == int(settings.main.channel_id))
async def handle_join_request(event: ChatJoinRequest):
    user_id = event.from_user.id

    try:
        user = await UserCRUD.get_user_by_tg_id(user_id)
        bot = event.bot
        if user and user.is_active:
            await event.approve()
            await bot.send_message(
                chat_id=user_id,
                text=(
                    "Ваш запрос на вступление в канал одобрен! "
                    "Ссылка на канал: https://t.me/+FJ3Xv4Lu5EM2ZGUy"
                ),
            )
            logging.info(f"Заявка одобрена для пользователя: {event.from_user.id}")

        else:
            await event.decline()
            await bot.send_message(
                chat_id=user_id,
                text="Извините, ваш запрос на вступление в канал отклонен. "
                "Видимо проблема с оплатой 😕",
            )

    except TelegramBadRequest as e:
        logging.error(e)

    except SQLAlchemyError as e:
        logging.error(e)

    except Exception as e:
        logging.error(e)


@router.chat_member()
async def on_user_join(event: ChatMemberUpdated):
    if (
        event.chat.id == int(settings.main.channel_id)
        and event.new_chat_member.status == "member"
    ):
        # Отправляем личное сообщение
        await event.bot.send_message(
            event.from_user.id,  # ID пользователя, который присоединился
            "Привет! Добро пожаловать в наш канал!",
        )


@router.chat_member()
async def on_user_join_or_leave(event: ChatMemberUpdated):
    user = event.from_user
    chat_id = event.chat.id
    status = event.new_chat_member.status

    if status == "member":  # Пользователь присоединился
        await event.bot.send_message(
            chat_id, f"{user.full_name} присоединился(лась) к каналу!"
        )
    elif status == "left":  # Пользователь покинул канал
        await event.bot.send_message(chat_id, f"{user.full_name} покинул(а) канал.")
    elif status == "kicked":  # Пользователь был кикнут
        await event.bot.send_message(
            chat_id, f"{user.full_name} был(а) исключён(а) из канала."
        )
