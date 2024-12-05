from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile

from aiogram.utils import markdown

from app.keyboards import PayCbData, PayActions, pay_kb

from app.routers.commands.main_commands import command_start_handler

from app.routers.channel_handlers import handle_new_member

from app.payment import payment_manager
from app.core.config import settings

router = Router(name=__name__)


@router.callback_query(PayCbData.filter(F.action == PayActions.back))
async def handle_back_button(call: CallbackQuery):
    await call.answer()
    await command_start_handler(message=call.message)
    await handle_new_member(call, name=call.message.from_user.first_name)


@router.callback_query(PayCbData.filter(F.action == PayActions.success))
async def handle_success(call: CallbackQuery):
    await call.answer()
    status = await payment_manager.get_payment_status(call.dat.payment_id)
    if status == "CONFIRMED":
        await handle_new_member(call, name=call.message.from_user.first_name)


# # Хэндлер нажатия кнопки "Оплатить"
# @router.callback_query(PayCbData.filter(F.action == PayActions.pay))
# async def pay_callback(call: CallbackQuery):
#     await call.answer()
#
#     user_id = call.from_user.id
#     payment_data = {
#         "user_id": user_id,
#         "amount": 10000,  # сумма платежа
#         "description": "Оплата доступа",
#         "success_url": f"https://latiy-trading.ru/success/{user_id}",  # URL после успешной оплаты
#         "webhook_url": f"{settings.web.base_url}/{settings.bot.token}",
#     }
#
#     async with call.session.post("", json=payment_data) as response:
#         if response.status == 200:
#             data = await response.json()
#             payment_link = data.get("payment_link")
#             await call.message.answer(f"Для оплаты перейдите по ссылке: {payment_link}")
#         else:
#             await call.message.answer("Ошибка при создании платежа. Попробуйте позже.")
#
#
# # Обработка webhook'а от платежной системы
# async def payment_webhook(request: web.Request):
#     try:
#         data = await request.json()
#
#         user_id = data["user_id"]
#         payment_status = data["status"]
#
#         if payment_status == "success":
#             await bot.send_message(
#                 user_id,
#                 "Оплата успешно завершена! Вот ваша ссылка: https://example.com/resource",
#             )
#
#         return web.Response(status=200)
#     except Exception as e:
#         logging.error(f"Ошибка при обработке webhook: {e}")
#         return web.Response(status=500)
