import logging

from aiogram import Bot

from aiohttp import web


# Обработчик для получения уведомлений о статусе платежа
async def handle_payment_notification(bot: Bot, request):
    try:
        data = await request.json()

        # Проверяем статус платежа и идентификатор
        if data.get("Success"):
            payment_id = data.get("PaymentId")
            status = data.get("Status")
            order_id = data.get(
                "OrderId"
            )  # Используем OrderId как идентификатор пользователя (или другое значение)

            # Логика обработки успешного платежа
            if status == "CONFIRMED":
                # Отправляем пользователю уведомление об успешной оплате
                await bot.send_message(
                    order_id,
                    "Ваш платеж успешно прошел! Мы начинаем обработку вашего заказа.",
                )
                # Логика предоставления услуги пользователю (например, активировать услугу)
                # Например, создать запись о заказе, обновить его статус и т.д.

            else:
                # Платеж не прошел, отправляем уведомление пользователю
                await bot.send_message(
                    order_id, "Оплата не прошла. Пожалуйста, попробуйте снова."
                )

            return web.json_response({"status": "ok"})
        else:
            # Платеж не был успешным
            return web.json_response({"status": "failed"})
    except Exception as e:
        logging.error(f"Error handling payment notification: {e}")
        return web.json_response({"status": "error"})
