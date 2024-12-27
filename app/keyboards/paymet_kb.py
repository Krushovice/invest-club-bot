from enum import IntEnum, auto

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class PayActions(IntEnum):
    pay = auto()
    help = auto()
    back = auto()


class PayCbData(CallbackData, prefix="pay"):
    action: PayActions
    payment_id: int | None = None


def pay_kb(payment: dict) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text="Оплата подписки",
        url=f"{payment['PaymentURL']}",
        callback_data=PayCbData(action=PayActions.pay),
    )

    builder.button(
        text="Помощь🆘",
        callback_data=PayCbData(action=PayActions.help),
    )
    builder.button(
        text="Назад🔙",
        callback_data=(
            PayCbData(
                action=PayActions.back,
            ).pack()
        ),
    )
    builder.adjust(1)

    return builder.as_markup()
