import datetime

from sqlalchemy import Integer, Date, ForeignKey, func, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    pay_id: Mapped[int] = mapped_column(BigInteger, unique=True)

    created_at: Mapped[datetime] = mapped_column(
        Date,
        default=datetime.datetime.today().strftime("%Y-%m-%d"),
        server_default=func.current_date(),
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
    )
    # Добавляем отношение многие к одному с моделью User
    user: Mapped["User"] = relationship(
        back_populates="payments",
        lazy="selectin",
    )
