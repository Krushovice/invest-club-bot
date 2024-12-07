import json
import logging

from aiogram import Bot
from aiogram.types import FSInputFile

from aiohttp import web

image_path = "app/utils/images/image3.JPEG"


#
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
        if status == "CONFIRMED":
            logging.info(f"Платеж подтвержден: {data}")

            # payment = save_user_payment()
            # tg_id = payment.user.tg_id
            # Отправка сообщения пользователю
            await bot.send_photo(
                chat_id=tg_id,
                photo=FSInputFile(image_path),
                caption="Ваш платеж успешно подтвержден!",
            )
            return web.json_response({"status": "ok"})
        else:
            logging.warning(f"Необработанный статус платежа: {status}")
            return web.json_response({"status": "unhandled status"})

    except Exception as e:
        logging.error(f"Ошибка в обработке вебхука: {e}", exc_info=True)
        return web.json_response({"status": "error"}, status=500)


async def save_user_payment(payment_id: int):
    # сохраняем платеж в базу данных и пробрасываем наверх
    pass
