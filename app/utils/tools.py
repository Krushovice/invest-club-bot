import logging

from aiogram import Bot

from aiohttp import web


# Обработчик для получения уведомлений о статусе платежа
async def handle_payment_notification(request, bot):
    try:
        # Лог входящего запроса
        logging.info(f"Handling request: {await request.text()}")

        # Парсим JSON
        data = await request.json()
        logging.info(f"Received data: {data}")

        # Проверяем обязательные поля
        if not all(
            key in data for key in ["Success", "PaymentId", "Status", "OrderId"]
        ):
            logging.error("Invalid request: Missing required fields")
            return web.json_response({"status": "invalid request"}, status=400)

        # Основная логика
        if data["Success"]:
            payment_id = data["PaymentId"]
            status = data["Status"]
            order_id = data["OrderId"]

            if status == "CONFIRMED":
                # Пример: Отправка сообщения через bot
                await bot.send_message(chat_id=order_id, text="Оплата прошла успешно!")
                logging.info(f"Payment confirmed for order {order_id}")
                return web.json_response({"status": "ok"})
        else:
            logging.warning("Payment failed")
            return web.json_response({"status": "failed"})

    except Exception as e:
        logging.error(f"Error processing request: {e}", exc_info=True)
        return web.json_response({"status": "error"}, status=500)
