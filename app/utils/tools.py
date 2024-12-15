import logging

import datetime

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import FSInputFile, Message

from aiohttp import web
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings

from app.core.database import UserSchema, UserCRUD

from app.keyboards import build_chat_kb


from app.core import User
from app.core.database import PaymentCRUD, PaymentSchema, UserUpdateSchema

from app.payment import parse_user_id_from_order_id

image_path = "app/utils/images/image3.JPEG"
ban_image_path = "app/utils/images/ban_image.png"


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
        count = 0
        if status == "CONFIRMED" and count == 0:
            count += 1
            user_id = await save_user_payment(
                payment_id=data["PaymentId"], order_id=data["OrderId"]
            )
            logging.info(f"Платеж подтвержден: {data}")
            if user_id:
                user = await UserCRUD.get_user(user_id=user_id)
                has_payments = True if user.chat_member else False

                invite_link = await check_chat_member(
                    tg_id=user.tg_id,
                    has_payments=has_payments,
                    bot=bot,
                )
                if invite_link:

                    await bot.send_photo(
                        chat_id=user.tg_id,
                        photo=FSInputFile(image_path),
                        caption="Ваш платеж успешно подтвержден! Ссылка на закрытый чат ниже",
                        reply_markup=build_chat_kb(
                            invite_link=invite_link,
                        ),
                    )
                    return web.json_response({"status": "ok"})
                else:
                    await bot.send_photo(
                        chat_id=user.tg_id,
                        photo=FSInputFile(image_path),
                        caption="Ваш платеж успешно подтвержден! Канал: <b>https://t.me/+FJ3Xv4Lu5EM2ZGUy</b>",
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


async def save_user_payment(payment_id: int, order_id: str):

    existing_payment = await PaymentCRUD.get_payment(payment_id)

    if existing_payment:
        return None

    else:
        user_id = parse_user_id_from_order_id(order_id)

        try:
            user = await UserCRUD.get_user(user_id=user_id)
            today = datetime.date.today()
            expired_date = today + datetime.timedelta(days=31)
            updated_user = UserUpdateSchema(
                tg_id=user.tg_id,
                is_active=True,
                chat_member=True,
                expired_at=expired_date,
            )
            await UserCRUD.update_user(
                user_id=user.id,
                user=updated_user,
            )

            pay_in = PaymentSchema(
                pay_id=payment_id,
                user_id=user_id,
            )
            await PaymentCRUD.create_payment(payment=pay_in)
            return user.id

        except SQLAlchemyError as e:
            logging.error(e)

        except Exception as e:
            logging.error(e)


async def check_chat_member(
    tg_id,
    bot: Bot,
    has_payments: bool = False,
):
    if has_payments:
        try:
            await bot.unban_chat_member(
                chat_id=settings.main.channel_id,
                user_id=tg_id,
                only_if_banned=True,
            )
            return None
        except TelegramBadRequest as e:
            logging.error(e)

    return settings.main.channel_link


async def register_user(message: Message):
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    username = message.from_user.username
    tg_id = message.from_user.id
    user_data = UserSchema(
        tg_id=tg_id,
        first_name=first_name,
        last_name=last_name,
        username=username,
    )
    try:
        user_exist = await UserCRUD.get_user_by_tg_id(tg_id)
        if not user_exist:
            user = await UserCRUD.create_user(user=user_data)
            return user
        return user_exist

    except SQLAlchemyError as e:
        logging.error(e)

    except Exception as e:
        logging.error(e)


async def check_user_subs(bot: Bot):
    users = await UserCRUD.get_users()
    for user in users:
        active = await get_user_subscribe(user)
        if not active:
            try:
                await bot.ban_chat_member(
                    chat_id=int(settings.main.channel_id),
                    user_id=user.tg_id,
                    revoke_messages=True,
                )
                await bot.send_photo(
                    chat_id=user.tg_id,
                    photo=FSInputFile(path=ban_image_path),
                    caption=f"Ваша подписка на канал закончилась {user.expired_at}. "
                    f"Оплатите пожалуйста доступ <b>/pay</b> 💰",
                )
            except TelegramBadRequest as e:
                logging.error(e)

            except Exception as e:
                logging.error(e)


async def reminder_subscribe(bot: Bot):
    users = await UserCRUD.get_users()

    today = datetime.date.today()
    for user in users:
        txt = (
            f"Ваша подписка на канал закончится {user.expired_at} и доступ будет ограничен. "
            "Не забудьте пожалуйста про оплату ✍️ /pay"
        )
        delta_days = (user.expired_at - today).days
        if user.is_active and 0 < delta_days < 3:
            await bot.send_message(
                chat_id=user.tg_id,
                text=txt,
            )


def schedule_tasks(bot: Bot):
    scheduler = AsyncIOScheduler(timezone="Asia/Vladivostok")

    scheduler.add_job(
        check_user_subs,
        trigger="cron",
        hour=datetime.datetime.now().hour,
        minute=datetime.datetime.now().minute + 1,
        start_date=datetime.datetime.now(),
        kwargs={"bot": bot},
        id="check_user_subs",
        replace_existing=True,
    )
    scheduler.add_job(
        reminder_subscribe,
        trigger="cron",
        hour=datetime.datetime.now().hour,
        minute=datetime.datetime.now().minute + 1,
        start_date=datetime.datetime.now(),
        kwargs={"bot": bot},
        id="reminder_subscribe",
        replace_existing=True,
    )

    scheduler.start()


async def get_user_subscribe(user: User):
    today = datetime.date.today()
    if user.expired_at < today and user.chat_member:
        try:
            user_in = UserUpdateSchema(
                tg_id=user.tg_id,
                is_active=False,
                chat_member=False,
            )
            await UserCRUD.update_user(user_id=user.id, user=user_in)
            return False
        except SQLAlchemyError as e:
            logging.error(e)

        except Exception as e:
            logging.error(e)
    else:
        return True
