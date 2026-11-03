import uuid

from decimal import Decimal

from sqlalchemy import (
    String,
    Numeric,
    ForeignKey,
    Boolean,
    CheckConstraint,
    text,
)

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import (
    Base,
    UUIDPrimaryKeyMixin,
    TimestampMixin,
)


class Bill(Base, UUIDPrimaryKeyMixin, TimestampMixin):

    __tablename__ = "bills"

    __table_args__ = (
        CheckConstraint(
            "subtotal >= 0",
            name="nonnegative_subtotal",
        ),
        CheckConstraint(
            "discount >= 0",
            name="nonnegative_discount",
        ),
        CheckConstraint(
            "tax_amount >= 0",
            name="nonnegative_tax",
        ),
        CheckConstraint(
            "grand_total >= 0",
            name="nonnegative_grand_total",
        ),
        CheckConstraint(
            "discount <= subtotal",
            name="discount_not_above_subtotal",
        ),
    )

    order_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("orders.id", ondelete="RESTRICT"),
        unique=True,
        nullable=False,
    )

    invoice_number: Mapped[str | None] = mapped_column(
        String(50),
        unique=True,
        nullable=True,
    )

    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    discount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=Decimal("0.00"),
        server_default=text("0"),
        nullable=False,
    )

    tax_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=Decimal("0.00"),
        server_default=text("0"),
        nullable=False,
    )

    grand_total: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    is_finalized: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=text("false"),
        nullable=False,
    )

    order: Mapped["Order"] = relationship(
        "Order",
        back_populates="bill",
    )

    payments: Mapped[list["Payment"]] = relationship(
        "Payment",
        back_populates="bill",
    )


class Payment(Base, UUIDPrimaryKeyMixin, TimestampMixin):

    __tablename__ = "payments"

    __table_args__ = (
        CheckConstraint(
            "amount > 0",
            name="positive_payment_amount",
        ),
    )

    bill_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("bills.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    payment_method: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    reference_number: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    payment_status: Mapped[str] = mapped_column(
        String(30),
        default="completed",
        server_default=text("'completed'"),
        nullable=False,
    )

    bill: Mapped["Bill"] = relationship(
        "Bill",
        back_populates="payments",
    )