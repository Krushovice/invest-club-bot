from sqlalchemy.ext.asyncio import AsyncSession

from .db import connection

from .base_classes import UserOrm, PaymentOrm

from .shemas import UserSchema, PaymentSchema
from app.core.models import User, Payment


class UserCRUD:

    @staticmethod
    @connection
    async def create_user(user: UserSchema, session: AsyncSession) -> User:
        user = await UserOrm.add_user(user_data=user.model_dump(), session=session)
        return user

    @staticmethod
    @connection
    async def get_user_by_tg_id(tg_id: int, session: AsyncSession) -> User:
        user = await UserOrm.find_one_or_none(tg_id=tg_id, session=session)
        return user

    @staticmethod
    @connection
    async def delete_user(user_id: int, session: AsyncSession) -> None:
        await UserOrm.delete(pk=user_id, session=session)


class PaymentCRUD:

    @staticmethod
    @connection
    async def create_payment(session: AsyncSession, payment: PaymentSchema) -> Payment:
        payment = await PaymentOrm.add_payment(
            session=session, pay_data=payment.model_dump()
        )
        return payment

    @staticmethod
    @connection
    async def get_payment_by_tg_id(session: AsyncSession, tg_id: int) -> Payment:
        payment = await PaymentOrm.find_one_or_none(
            session=session,
            tg_id=tg_id,
        )
        return payment

    @staticmethod
    @connection
    async def delete_payment(session: AsyncSession, payment_id: int) -> None:
        await PaymentOrm.delete(session=session, pk=payment_id)
