import asyncio


from aiogram import Bot, Dispatcher

from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.core.logging import setup_logger

from app.core.config import settings

from app.commands import router as commands_router

logger = setup_logger(__name__)


async def main():
    try:
        dp = Dispatcher()
        bot = Bot(
            token=settings.bot_token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )

        dp.include_router(commands_router)
        await dp.start_polling(bot)

    except Exception as e:
        logger.error(e)


# Press the green button in the gutter to run the script.
if __name__ == "__main__":
    asyncio.run(main())

# webhook example

# from aiohttp import web
# from aiogram import Bot, Dispatcher
#
# API_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
# WEBHOOK_PATH = "/webhook"
# WEBHOOK_URL = f"https://your-domain.com{WEBHOOK_PATH}"
#
# bot = Bot(token=API_TOKEN)
# dp = Dispatcher()
#
# # Обработка входящих апдейтов
# async def handle_update(request: web.Request):
#     update = await request.json()
#     await bot.process_update(update)
#     return web.Response()
#
# app = web.Application()
# app.router.add_post(WEBHOOK_PATH, handle_update)

# async def set_webhook():
#     await bot.set_webhook(WEBHOOK_URL)
# #
# if __name__ == "__main__":
#     web.run_app(app, host="0.0.0.0", port=8443)
