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

from app.core.logging import setup_logger

image_path = "app/utils/images/image3.JPEG"
ban_image_path = "app/utils/images/ban_image.png"
logger = setup_logger(__name__)


# Обработчик для получения уведомлений о статусе платежа
async def handle_payment_notification(request, bot: Bot):
    try:
        # Получаем JSON из запроса
        data = await request.json()
        logger.info(f"Получены данные: {data}")

        # Проверяем наличие обязательных полей
        required_fields = ["Success", "PaymentId", "Status", "OrderId"]
        if not all(key in data for key in required_fields):
            logger.error("Отсутствуют обязательные поля в запросе")
            return web.json_response(
                {"status": "missing required fields"},
                status=400,
            )

        # Извлекаем статус
        status = data["Status"]
        logger.info(f"Обработка платежа со статусом: {status}")
        count = 0

        # Проверка успешного платежа
        if status == "CONFIRMED" and count == 0:
            # Сохраняем платеж и получаем ID пользователя
            user_id = await save_user_payment(
                payment_id=data["PaymentId"],
                order_id=data["OrderId"],
            )

            if user_id:
                # Получаем данные пользователя
                user = await UserCRUD.get_user(user_id=user_id)
                if not user:
                    logger.error(f"Пользователь с ID {user_id} не найден")
                    return web.json_response(
                        {"status": "error", "message": "user not found"},
                        status=404,
                    )

                chat_member = user.chat_member is True
                invite_link = settings.main.channel_link

                if chat_member:
                    # Если пользователь уже в чате, разбаниваем
                    await unban_old_user(
                        bot=bot,
                        channel_id=int(settings.main.channel_id),
                        user_id=user.tg_id,
                    )
                else:
                    # Если пользователь новый, отправляем сообщение с приглашением
                    await bot.send_photo(
                        chat_id=user.tg_id,
                        photo=FSInputFile(image_path),
                        caption="Ваш платеж успешно подтвержден! Ссылка на закрытый чат ниже:",
                        reply_markup=build_chat_kb(invite_link=invite_link),
                    )

                return web.json_response({"status": "ok"})
            else:
                logger.warning("Платеж уже обработан")
                return web.json_response(
                    {"status": "ok", "text": "Платеж уже обработан"}
                )

        # Необработанный статус платежа
        logger.warning(f"Необработанный статус платежа: {status}")
        return web.json_response({"status": "unhandled status"})

    except Exception as e:
        # Логирование ошибок
        logger.error(f"Ошибка в обработке вебхука: {e}", exc_info=True)
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
            logger.error(e)

        except Exception as e:
            logger.error(e)


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
        user = await UserCRUD.get_user_by_tg_id(tg_id)
        if not user:
            user = await UserCRUD.create_user(user=user_data)
        return user

    except SQLAlchemyError as e:
        logger.error(e)

    except Exception as e:
        logger.error(e)


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
                logger.error(e)

            except Exception as e:
                logger.error(e)


async def reminder_subscribe(bot: Bot):
    users = await UserCRUD.get_users()

    today = datetime.date.today()
    for user in users:
        txt = (
            f"Ваша подписка на канал закончится {user.expired_at} и доступ будет ограничен. "
            "Не забудьте пожалуйста про оплату ✍️ /pay"
        )
        if user.is_active:
            delta_days = (user.expired_at - today).days
            if 0 < delta_days < 3:
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
    if user.is_active:
        if user.expired_at < today:
            try:
                user_in = UserUpdateSchema(
                    tg_id=user.tg_id,
                    is_active=False,
                    chat_member=False,
                )
                await UserCRUD.update_user(user_id=user.id, user=user_in)
                return False
            except SQLAlchemyError as e:
                logger.error(e)

            except Exception as e:
                logger.error(e)
        else:
            return True


async def unban_old_user(
    bot: Bot,
    channel_id: int,
    user_id: int,
):
    try:
        # Снимаем бан
        status = await bot.unban_chat_member(
            chat_id=channel_id,
            user_id=user_id,
            only_if_banned=True,
        )
        invite_link = settings.main.channel_link
        # Проверяем статус после снятия бана
        member_after = await bot.get_chat_member(
            chat_id=channel_id,
            user_id=user_id,
        )
        if status and member_after.status == "left":
            print("Пользователь разбанен!")
            await bot.send_photo(
                chat_id=user_id,
                photo=FSInputFile(image_path),
                caption=f"Ваш платеж успешно подтвержден! Канал: {invite_link}",
            )
            return web.json_response({"status": "ok"})

        else:
            print("Функция работает неверно")
            return False

    except TelegramBadRequest as e:
        logger.error(e)

    except Exception as e:
        logger.error(e)
