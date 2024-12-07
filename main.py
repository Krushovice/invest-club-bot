import asyncio
import logging
import functools

from aiogram import Bot, Dispatcher

from aiogram.client.default import DefaultBotProperties

from aiohttp import web
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from app.core.config import settings

from app.routers import router as main_router

from app.utils import handle_payment_notification

dp = Dispatcher()
bot = Bot(
    token=settings.bot.token,
    default=DefaultBotProperties(
        parse_mode=settings.bot.parse_mode,
    ),
)


# Функция, которая будет вызвана при запуске бота
async def on_startup() -> None:

    # Устанавливаем вебхук для приема сообщений через заданный URL
    await bot.set_webhook(
        f"{settings.web.base_url}{settings.web.main_path}",
    )
    # Отправляем сообщение администратору о том, что бот был запущен
    await bot.send_message(
        chat_id=settings.main.admin_id,
        text="Бот запущен!",
    )


# Функция, которая будет вызвана при остановке бота
async def on_shutdown() -> None:
    # Отправляем сообщение администратору о том, что бот был остановлен
    await bot.send_message(
        chat_id=settings.main.admin_id,
        text="Бот остановлен!",
    )
    # Удаляем вебхук и, при необходимости, очищаем ожидающие обновления
    await bot.delete_webhook(drop_pending_updates=True)
    # Закрываем сессию бота, освобождая ресурсы
    await bot.session.close()


def main() -> None:

    # Подключаем маршрутизатор (роутер) для обработки сообщений
    dp.include_router(main_router)

    # Регистрируем функцию, которая будет вызвана при старте бота
    dp.startup.register(on_startup)

    # Регистрируем функцию, которая будет вызвана при остановке бота
    dp.shutdown.register(on_shutdown)

    # Создаем веб-приложение на базе aiohttp
    app = web.Application()

    # Устанавливаем обработчик платежей
    partial_handler = functools.partial(
        handle_payment_notification,
        bot=bot,
    )
    app.router.add_post(
        f"{settings.web.pay_path}",
        handler=partial_handler,
    )

    # Настраиваем обработчик запросов для работы с вебхуком
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    # Регистрируем обработчик запросов на определенном пути
    webhook_requests_handler.register(
        app,
        path=f"{settings.web.main_path}",
    )

    # Настраиваем приложение и связываем его с диспетчером и ботом
    setup_application(app, dp, bot=bot)

    # Запускаем веб-сервер на указанном хосте и порте
    web.run_app(
        app,
        host=settings.web.host,
        port=settings.web.port,
    )


if __name__ == "__main__":
    # Настраиваем логирование (информация, предупреждения, ошибки) и выводим их в консоль
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger(__name__)
    main()
