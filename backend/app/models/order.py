import enum
import uuid

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    String,
    Text,
    Numeric,
    Integer,
    DateTime,
    ForeignKey,
    Enum as SQLEnum,
    CheckConstraint,
    text,
)

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import (
    Base,
    UUIDPrimaryKeyMixin,
    TimestampMixin,
)


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    PREPARING = "preparing"
    READY = "ready"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Order(Base, UUIDPrimaryKeyMixin, TimestampMixin):

    __tablename__ = "orders"

    created_by_user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    device_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("devices.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    customer_name: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True,
    )

    customer_phone: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    customer_location: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[OrderStatus] = mapped_column(
        SQLEnum(
            OrderStatus,
            name="order_status",
            values_callable=lambda enum_cls: [
                item.value for item in enum_cls
            ],
        ),
        default=OrderStatus.PENDING,
        server_default=text("'pending'"),
        nullable=False,
    )

    version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        server_default=text("1"),
        nullable=False,
    )

    ordered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    created_by: Mapped["User"] = relationship(
        "User",
        back_populates="orders",
    )

    device: Mapped["Device"] = relationship(
        "Device",
        back_populates="orders",
    )

    items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
    )

    bill: Mapped["Bill | None"] = relationship(
        "Bill",
        back_populates="order",
        uselist=False,
    )


class OrderItem(Base, UUIDPrimaryKeyMixin, TimestampMixin):

    __tablename__ = "order_items"

    __table_args__ = (
        CheckConstraint(
            "quantity > 0",
            name="positive_quantity",
        ),
        CheckConstraint(
            "unit_price >= 0",
            name="nonnegative_unit_price",
        ),
        CheckConstraint(
            "line_total >= 0",
            name="nonnegative_line_total",
        ),
    )

    order_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    menu_item_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("menu_items.id", ondelete="RESTRICT"),
        nullable=False,
    )

    # Preserve the name at the time of purchase.
    item_name_tamil: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    item_name_english: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    quantity: Mapped[Decimal] = mapped_column(
        Numeric(10, 3),
        nullable=False,
    )

    # Price snapshot at the time the order was created.
    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    line_total: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    order: Mapped["Order"] = relationship(
        "Order",
        back_populates="items",
    )