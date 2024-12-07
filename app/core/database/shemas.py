from typing import List
from pydantic import BaseModel, ConfigDict
from datetime import date


class PaymentSchema(BaseModel):
    pay_id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class UserSchema(BaseModel):
    tg_id: int
    first_name: str
    last_name: str
    payments: List[PaymentSchema] | None = None

    model_config = ConfigDict(from_attributes=True)
