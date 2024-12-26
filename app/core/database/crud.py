from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from .db import connection

from .base_classes import UserOrm, PaymentOrm

from .schemas import UserSchema, PaymentSchema, UserUpdateSchema, PaymentUpdateSchema
from app.core.models import User, Payment


class UserCRUD:

    @staticmethod
    @connection
    async def create_user(
        user: UserSchema,
        session: AsyncSession,
    ) -> User:
        user = await UserOrm.add_user(user_data=user.model_dump(), session=session)
        return user

    @staticmethod
    @connection
    async def get_user(
        user_id: int,
        session: AsyncSession,
    ) -> User:
        user = await UserOrm.get_user(user_id=user_id, session=session)
        return user

    @staticmethod
    @connection
    async def get_user_by_tg_id(
        tg_id: int,
        session: AsyncSession,
    ) -> User:
        user = await UserOrm.get_user_by_tg_id(tg_id=tg_id, session=session)
        return user

    @staticmethod
    @connection
    async def get_user_by_id_with_sub_model(
        tg_id: int,
        session: AsyncSession,
    ) -> User:
        user = await UserOrm.get_user_with_related_model_by_tg_id(
            tg_id=tg_id,
            session=session,
        )
        return user

    @staticmethod
    @connection
    async def get_users(session: AsyncSession) -> List[User]:
        users = await UserOrm.find_all(session=session)
        return users

    @staticmethod
    @connection
    async def update_user(
        user_id: int,
        user: UserUpdateSchema,
        session: AsyncSession,
    ) -> User:
        user = await UserOrm.update(
            session=session,
            pk=user_id,
            **user.model_dump(exclude_none=True),
        )
        return user

    @staticmethod
    @connection
    async def delete_user(user_id: int, session: AsyncSession) -> None:
        await UserOrm.delete(pk=user_id, session=session)


class PaymentCRUD:

    @staticmethod
    @connection
    async def create_payment(payment: PaymentSchema, session: AsyncSession) -> Payment:
        payment = await PaymentOrm.add_payment(
            pay_data=payment.model_dump(),
            session=session,
        )
        return payment

    @staticmethod
    @connection
    async def get_payment(
        payment_id: int,
        session: AsyncSession,
    ) -> Payment:
        payment = await PaymentOrm.get_payment(
            session=session,
            payment_id=payment_id,
        )
        return payment

    @staticmethod
    @connection
    async def get_payment_with_sub_model(
        payment_id: int,
        session: AsyncSession,
    ) -> Payment:
        payment = await PaymentOrm.get_payment_with_related_model(
            payment_id=payment_id,
            session=session,
        )
        return payment

    @staticmethod
    @connection
    async def update_payment(
        payment_id: int,
        pay_data: PaymentUpdateSchema,
        session: AsyncSession,
    ) -> Payment:
        pay = await PaymentOrm.update(
            session=session,
            pk=payment_id,
            **pay_data.model_dump(),
        )
        return pay

    @staticmethod
    @connection
    async def delete_payment(
        payment_id: int,
        session: AsyncSession,
    ) -> None:
        await PaymentOrm.delete(
            pk=payment_id,
            session=session,
        )
