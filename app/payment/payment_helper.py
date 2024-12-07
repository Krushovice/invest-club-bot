import aiohttp


from .tools import generate_token, create_token

from app.core.config import settings

from app.core.logging import setup_logger

logger = setup_logger(__name__)


class PaymentManager:
    def __init__(self, terminal_key, secret_key):
        self.terminal_key = terminal_key
        self.secret_key = secret_key
        self.api_url = "https://securepay.tinkoff.ru/v2/"

    async def init_payment(
        self,
        amount,
        order_id,
        description,
        receipt,
    ):

        data = {
            "TerminalKey": self.terminal_key,
            "Amount": amount,
            "OrderId": order_id,
            "PayType": "O",
            "NotificationURL": "https://9229-82-162-122-212.ngrok-free.app/payment_webhook",
            "DATA": {
                "QR": "true",
            },
            "Description": description,
        }

        token = generate_token(
            data=data,
            password=self.secret_key,
        )

        data["Token"] = token
        data["Receipt"] = receipt

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    self.api_url + "Init",
                    json=data,
                    ssl=False,
                ) as response:

                    if response.status != 200:
                        logger.error(
                            f"Ошибка в инициализации платежа: {await response.text()}"
                        )
                        return None
                    else:
                        result = await response.json(
                            content_type="application/json",
                        )
                        if result.get("Success"):
                            return result
                        else:
                            logger.error(f"Ошибка в результате платежа: {result}")
                            return None

            except aiohttp.ContentTypeError:
                text = await response.text()
                logger.error(f"Ошибка обработки JSON: {text}")
                return None

            except Exception as e:
                logger.error(e)

    async def check_payment_status(self, payment_id):
        token = create_token(str(payment_id))
        data = {
            "TerminalKey": self.terminal_key,
            "PaymentId": payment_id,
            "Token": token,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.api_url + "GetState",
                json=data,
                ssl=False,
            ) as response:
                result = await response.json()
                return result

    async def get_payment_info(self, payment_id):
        token = create_token(str(payment_id))
        data = {
            "TerminalKey": self.terminal_key,
            "PaymentId": payment_id,
            "Token": token,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.api_url + "GetReceipt",
                json=data,
                ssl=False,
            ) as response:
                result = await response.json()
                return result

    async def get_qr(self, payment_id):

        data = {
            "TerminalKey": self.terminal_key,
            "PaymentId": payment_id,
            "DataType": "PAYLOAD",
        }
        token = generate_token(
            data=data,
            password=self.secret_key,
        )
        data.update({"Token": token})

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.api_url + "GetQr",
                json=data,
                ssl=False,
            ) as response:
                result = await response.json()
                if result["Sucess"]:
                    return result["Data"]
                return None

    async def get_confirm_operation(self, payments: list):

        data = {
            "TerminalKey": self.terminal_key,
            "CallbackUrl": settings.EMAIL,
            "PaymentIdList": payments,
        }
        token = generate_token(
            data=data,
            password=self.secret_key,
        )
        data.update({"Token": token})
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.api_url + "getConfirmOperation",
                json=data,
                ssl=False,
            ) as response:
                result = await response.json()
                return result


payment_manager = PaymentManager(
    terminal_key=settings.pay.terminal_key,
    secret_key=settings.pay.secret,
)
