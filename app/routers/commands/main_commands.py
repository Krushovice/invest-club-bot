from aiogram import Router
from aiogram.utils import markdown

from aiohttp.http_exceptions import HttpBadRequest

from aiogram.exceptions import TelegramBadRequest

from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile

from app.core.logging import setup_logger

from app.payment import (
    payment_manager,
    generate_order_number,
    get_receipt,
)

from app.keyboards import pay_kb


router = Router(name=__name__)
logger = setup_logger(__name__)

file_path1 = "app/utils/images/image1.jpg"
file_path2 = "app/utils/images/pay_image.jpg"


@router.message(CommandStart())
async def command_start_handler(message: Message):
    try:
        name = message.from_user.first_name
        last_name = message.from_user.last_name

        text = (
            f"Здравствуй, <b>{name}, {last_name}</b>👋, всего один шаг отделяет тебя от присоединения к нашей стратегии следования! "
            f"Для того, чтобы присоединиться к <i>закрытому</i> инвест-клубу 💰,"
            "необходимо оплатить ежемесячную подписку по команде <b>/pay</b>."
        )
        await message.answer_photo(
            photo=FSInputFile(file_path1),
            caption=text,
        )

    except TelegramBadRequest as e:
        logger.error(e)

    except KeyboardInterrupt as e:
        logger.error(f"Бот был остановлен администратором: {e}")

    except Exception as e:
        logger.error(e)


@router.message(Command("pay", prefix="!/"))
async def command_pay_handler(message: Message):
    try:
        payment = await payment_manager.init_payment(
            tg_id=message.from_user.id,
            amount=100000,
            order_id=generate_order_number(),
            description=f"Оплата пользователя № {message.from_user.id}",
            receipt=get_receipt(price=100000),
        )
        if payment:
            msg = markdown.text(
                markdown.hbold(f"💰 Сумма: 1000 руб"),
                markdown.hitalic("Для оплаты перейдите по ссылке ниже ⬇️"),
                markdown.hitalic("Как только оплатите, через пару секунд 'Жми✅'"),
                sep="\n\n",
            )
            await message.answer_photo(
                photo=FSInputFile(file_path2),
                caption=msg,
                reply_markup=pay_kb(payment),
            )

    except HttpBadRequest as e:
        logger.error(f"Ошибка http запроса к апи: {e}")

    except TelegramBadRequest as e:
        logger.error(e)

    except Exception as e:
        logger.error(e)
