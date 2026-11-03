from datetime import datetime

from sqlalchemy import (
    String,
    Boolean,
    DateTime,
    ForeignKey,
    text,
)

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import (
    Base,
    UUIDPrimaryKeyMixin,
    TimestampMixin,
)


class Device(Base, UUIDPrimaryKeyMixin, TimestampMixin):

    __tablename__ = "devices"

    device_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    device_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        server_default=text("true"),
        nullable=False,
    )

    last_sync_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    orders: Mapped[list["Order"]] = relationship(
        "Order",
        back_populates="device",
    )