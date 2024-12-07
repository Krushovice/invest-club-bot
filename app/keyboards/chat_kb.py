from enum import IntEnum, auto
from sys import prefix

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class ChatActions(IntEnum):
    join = auto()
    back = auto()


class ChatCbData(CallbackData, prefix="chat"):
    action: ChatActions


def build_chat_kb(invite_link: str) -> InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()

    builder.button(
        text="Присоединиться к каналу",
        url=invite_link,
        callback_data=ChatCbData(action=ChatActions.join),
    )

    builder.button(
        text="Назад🔙",
        callback_data=(
            ChatCbData(
                action=ChatActions.back,
            ).pack()
        ),
    )
    builder.adjust(1)

    return builder.as_markup()
