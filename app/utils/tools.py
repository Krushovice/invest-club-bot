import logging
import functools
import asyncio
import datetime

from aiogram import Bot
from aiogram.types import FSInputFile, Message

from aiohttp import web

from app.core.config import settings

from app.core.database import UserSchema, UserCRUD

from app.keyboards import build_chat_kb
from core.database import PaymentCRUD

image_path = "app/utils/images/image3.JPEG"
ban_image_path = "app/utils/images/ban_image.png"


def async_repeat(interval):
    """
    Декоратор для асинхронного вызова функции с заданным интервалом.
    """

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            while True:
                await func(*args, **kwargs)
                await asyncio.sleep(interval)  # Ожидание заданного интервала

        return wrapper

    return decorator


# Обработчик для получения уведомлений о статусе платежа
async def handle_payment_notification(request, bot: Bot):
    try:

        logging.info(f"Получен запрос: {await request.text()}")

        data = await request.json()

        logging.info(f"Парсинг JSON успешен: {data}")

        # Проверяем наличие обязательных полей
        if not all(
            key in data for key in ["Success", "PaymentId", "Status", "OrderId"]
        ):
            logging.error("Отсутствуют обязательные поля в запросе")
            return web.json_response({"status": "missing required fields"}, status=400)

        status = data["Status"]
        # если платеж успешен и его еще нет в бд
        if status == "CONFIRMED":
            payment = await save_user_payment(payment_id=data["PaymentId"])
            logging.info(f"Платеж подтвержден: {data}")
            if payment:
                invite_link = await work_with_chat_member(payment=payment, bot=bot)
                await bot.send_photo(
                    chat_id=payment.user.tg_id,
                    photo=FSInputFile(image_path),
                    caption="Ваш платеж успешно подтвержден! Ссылка на закрытый чат ниже",
                    reply_markup=build_chat_kb(invite_link=invite_link),
                )
                return web.json_response({"status": "ok"})
            else:
                logging.info(f"Платеж {data["PaymentId"]} уже обработан")
                return web.json_response(
                    {"status": "ok", "text": "Платеж уже обработан"}
                )
        else:
            logging.warning(f"Необработанный статус платежа: {status}")
            return web.json_response({"status": "unhandled status"})

    except Exception as e:
        logging.error(f"Ошибка в обработке вебхука: {e}", exc_info=True)
        return web.json_response({"status": "error"}, status=500)


async def save_user_payment(payment_id: int):
    # сохраняем платеж в базу данных и пробрасываем наверх
    check_for_exist = await PaymentCRUD.get_payment_by_pay_id(payment_id)

    if check_for_exist:
        return None

    payment = await PaymentCRUD.create_payment(payment_id=payment_id)
    return payment


async def work_with_chat_member(payment, bot: Bot):
    if payment.user.payments:
        await bot.unban_chat_member(
            chat_id=settings.main.channel_id,
            user_id=payment.user.tg_id,
            only_if_banned=True,
        )
    else:
        chat_link = await bot.create_chat_invite_link(
            chat_id=settings.main.channel_id,
            name=f"Инвайт сслыка юзера: {payment.user.tg_id}",
        )
        return chat_link.invite_link


async def register_user(message: Message):
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    tg_id = message.from_user.id
    user_data = UserSchema(
        tg_id=tg_id,
        first_name=first_name,
        last_name=last_name,
    )
    user_exist = await UserCRUD.get_user_by_tg_id(tg_id)
    if not user_exist:
        user = await UserCRUD.create_user(user=user_data)
        return user
    return user_exist


@async_repeat(interval=24 * 3600)
async def check_user_subs(bot: Bot):
    users = await UserCRUD.get_users()
    today = datetime.date.today()
    for user in users:
        if user.expired_at < today and not user.is_active:
            await bot.ban_chat_member(
                chat_id=settings.main.channel_id,
                user_id=user.tg_id,
                revoke_messages=True,
            )
            await bot.send_photo(
                chat_id=user.tg_id,
                photo=FSInputFile(path=ban_image_path),
                caption=f"Ваша подписка на канал закончилась {user.expired_at}. "
                f"Оплатите пожалуйста доступ /pay 💰",
            )
