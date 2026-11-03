from decimal import Decimal
import uuid

from sqlalchemy import (
    String,
    Boolean,
    ForeignKey,
    Numeric,
    text,
)

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import (
    Base,
    UUIDPrimaryKeyMixin,
    TimestampMixin,
)


class Category(Base, UUIDPrimaryKeyMixin, TimestampMixin):

    __tablename__ = "categories"

    name_tamil: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    name_english: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    display_order: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        server_default=text("true"),
        nullable=False,
    )

    menu_items: Mapped[list["MenuItem"]] = relationship(
        "MenuItem",
        back_populates="category",
    )


class MenuItem(Base, UUIDPrimaryKeyMixin, TimestampMixin):

    __tablename__ = "menu_items"

    category_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("categories.id", ondelete="RESTRICT"),
        nullable=False,
    )

    name_tamil: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    name_english: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    image_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    is_available: Mapped[bool] = mapped_column(
        Boolean,
        server_default=text("true"),
        nullable=False,
    )

    category: Mapped["Category"] = relationship(
        "Category",
        back_populates="menu_items",
    )
