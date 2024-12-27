from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from datetime import date


class PaymentSchema(BaseModel):
    pay_id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class PaymentUpdateSchema(BaseModel):
    is_successful: Optional[bool] = False

    model_config = ConfigDict(from_attributes=True)


class UserSchema(BaseModel):
    tg_id: int
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    payments: List[PaymentSchema] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class UserUpdateSchema(UserSchema):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    expired_at: Optional[date] = None
    is_active: Optional[bool] = None
    chat_member: Optional[bool] = None
    payments: List[PaymentSchema] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
