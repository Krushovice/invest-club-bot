import re
import uuid
import hashlib
import datetime
import logging

from app.core.logging import setup_logger

from app.core.config import Settings

settings = Settings()

logger = setup_logger(__name__)


def generate_order_number(user_id: int, max_length: int = 30):
    # Генерируем UUID (универсальный уникальный идентификатор)
    # Используем только первые 8 символов UUID для краткости
    order_id = uuid.uuid4().hex[:8]
    order_number = f"{user_id}_{order_id}"

    # Проверяем, не превышает ли длина max_length
    if len(order_number) > max_length:
        # Если превышает, хэшируем длинный идентификатор
        hash_part = hashlib.sha256(order_number.encode()).hexdigest()[:8]
        order_number = f"{user_id}_{hash_part}"

    return order_number


def get_receipt(price):
    data = {
        "Taxation": "usn_income",
        "Email": "list90@list.ru",
        "Items": [
            {
                "Name": "Подписка на канал",
                "Price": price,
                "Quantity": 1.0,
                "Amount": price,
                "PaymentMethod": "full_payment",
                "PaymentObject": "service",
                "Tax": "none",
            },
        ],
    }
    return data


def create_token(payment_id):

    tokentr = (
        settings.pay.tinkoff_secret + payment_id + settings.pay.tinkoff_terminal_key
    )
    tokensha256 = str(hashlib.sha256(tokentr.encode()).hexdigest())
    return tokensha256


def generate_token(data, password):

    data["Password"] = password

    # Исключаем вложенные объекты и массивы из расчета токена
    filtered_data = {k: v for k, v in data.items() if not isinstance(v, (dict, list))}

    # Конвертация словаря в отсортированный список кортежей (ключ, значение)
    sorted_data = sorted(filtered_data.items(), key=lambda x: x[0])
    # Конкатенация значений пар в одну строку
    concatenated_values = "".join([str(value) for _, value in sorted_data])

    hashed_token = hashlib.sha256(concatenated_values.encode("utf-8")).hexdigest()

    return str(hashed_token)


def check_payment_date(data: str) -> bool:
    today = datetime.datetime.today().date()
    pattern = r":\s*(\d{4}-\d{2}-\d{2})"

    # Извлекаем дату из строки, если она присутствует
    match = re.search(pattern, data)
    if match:
        string_date = match.group(1)
        # Преобразование строки даты в объект datetime
        pay_date = datetime.datetime.strptime(string_date, "%Y-%m-%d").date()
        if pay_date == today:
            return True
    return False


def check_payment(payment) -> bool:
    return True if payment["Status"] == "CONFIRMED" else False


def parse_user_id_from_order_id(order_id: str) -> int | None:
    try:
        user_id, _ = order_id.split("_", 1)
        return int(user_id)
    except ValueError:
        logging.error(f"Не удалось извлечь user_id из OrderId: {order_id}")
        return None
