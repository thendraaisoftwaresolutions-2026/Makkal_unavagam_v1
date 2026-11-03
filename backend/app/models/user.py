import enum

from sqlalchemy import (
    String,
    Boolean,
    Enum as SQLEnum,
    text,
)

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import (
    Base,
    UUIDPrimaryKeyMixin,
    TimestampMixin,
)


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    CASHIER = "cashier"


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):

    __tablename__ = "users"

    username: Mapped[str] = mapped_column(
        String(80),
        unique=True,
        index=True,
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole, name="user_role"),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        server_default=text("true"),
        nullable=False,
    )

    orders: Mapped[list["Order"]] = relationship(
        "Order",
        back_populates="created_by",
    )