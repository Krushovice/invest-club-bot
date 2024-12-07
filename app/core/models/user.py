import datetime

from sqlalchemy import (
    BigInteger,
    Integer,
    String,
    Date,
    func,
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .payment import Payment


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    tg_id: Mapped[int] = mapped_column(
        BigInteger(),
        unique=True,
        index=True,
    )

    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))

    created_at: Mapped[datetime] = mapped_column(
        Date,
        default=datetime.datetime.today(),
        server_default=func.current_date(),
    )

    is_active: Mapped[bool] = mapped_column(default=False)

    payments: Mapped[list["Payment"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    @hybrid_property
    def created_date(self):
        if self.created_at:
            return self.created_at.strftime("%Y-%m-%d")
        else:
            return None

    def __str__(self):
        return f"User(id={self.id!r}, is_active={self.is_active!r})"

    def __repr__(self) -> str:
        return str(self)
