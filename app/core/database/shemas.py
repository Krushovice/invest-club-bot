from typing import List
from pydantic import BaseModel, ConfigDict, Field
from datetime import date


class PaymentSchema(BaseModel):
    pay_id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class UserSchema(BaseModel):
    tg_id: int
    first_name: str | None = None
    last_name: str | None = None
    payments: List[PaymentSchema] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class UserUpdateSchema(UserSchema):
    first_name: str | None = None
    last_name: str | None = None
    expired_at: date | None = None
    is_active: bool | None = None
    chat_member: bool | None = None
    payments: List[PaymentSchema] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
