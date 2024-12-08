from typing import List, Any, Dict

from sqlalchemy import select, Result
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import User, Payment


class BaseOrm:
    model = None  # Устанавливается в дочернем классе

    @classmethod
    async def add(cls, session: AsyncSession, **values):
        # Добавить одну запись
        new_instance = cls.model(**values)
        session.add(new_instance)
        try:
            await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()
            raise e
        return new_instance

    @classmethod
    async def get_one_or_none_by_id(cls, data_id: int, session: AsyncSession):
        query = select(cls.model).filter_by(id=data_id)
        result = await session.execute(query)
        record = result.scalar_one_or_none()
        return record

    @classmethod
    async def find_one_or_none(cls, session: AsyncSession, **filter_by):
        query = select(cls.model).filter_by(**filter_by)
        result = await session.execute(query)
        record = result.scalar_one_or_none()
        return record

    @classmethod
    async def find_all(cls, session: AsyncSession, **filter_by):
        query = select(cls.model).filter_by(**filter_by)
        result = await session.execute(query)
        records = result.scalars().all()
        return records

    @classmethod
    async def update(
        cls,
        session: AsyncSession,
        pk: int,
        **kwargs,
    ):

        query = select(cls.model).filter_by(id=pk)

        result: Result = await session.execute(query)

        record: cls.model | None = result.scalar_one_or_none()

        for key, value in kwargs.items():
            setattr(record, key, value)

        session.add(record)
        await session.commit()
        return record

    @classmethod
    async def delete(cls, session: AsyncSession, pk: int):
        query = select(cls.model).filter_by(id=pk)
        res: Result = await session.execute(query)
        inst = res.scalar()
        await session.delete(inst)
        await session.commit()


class UserOrm(BaseOrm):
    model = User

    @classmethod
    async def add_user(cls, session: AsyncSession, user_data: dict) -> User:
        # Создаем пользователя из переданных данных
        user = cls.model(
            tg_id=user_data["tg_id"],
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
        )
        session.add(user)
        await session.commit()
        return user

    @classmethod
    async def get_user(cls, session: AsyncSession, user_id: int) -> User:
        user = await cls.get_one_or_none_by_id(data_id=user_id, session=session)
        return user


class PaymentOrm(BaseOrm):
    model = Payment

    @classmethod
    async def add_payment(cls, session: AsyncSession, pay_data: dict) -> Payment:
        # Создаем пользователя из переданных данных
        payment = cls.model(
            pay_id=pay_data["payment_id"],
            user_id=pay_data["user_id"],
        )
        session.add(payment)
        await session.commit()
        return payment

    @classmethod
    async def get_payment(cls, session: AsyncSession, payment_id: int) -> Payment:
        payment = await cls.get_one_or_none_by_id(data_id=payment_id, session=session)
        return payment
