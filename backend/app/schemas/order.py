
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.order import OrderStatus


class OrderItemCreate(BaseModel):
    menu_item_id: UUID
    quantity: Decimal = Field(
        gt=0,
        max_digits=10,
        decimal_places=3,
    )


class OrderCreate(BaseModel):
    device_id: UUID
    customer_name: str | None = Field(default=None, max_length=120)
    customer_phone: str | None = Field(default=None, max_length=20)
    customer_location: str | None = Field(default=None, max_length=255)
    notes: str | None = None

    items: list[OrderItemCreate] = Field(
        min_length=1,
        max_length=50,
    )


class OrderItemResponse(BaseModel):
    id: UUID
    menu_item_id: UUID
    item_name_tamil: str
    item_name_english: str
    quantity: Decimal
    unit_price: Decimal
    line_total: Decimal

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    id: UUID
    device_id: UUID
    created_by_user_id: UUID
    customer_name: str | None
    customer_phone: str | None
    customer_location: str | None
    notes: str | None
    status: OrderStatus
    version: int
    ordered_at: datetime
    items: list[OrderItemResponse]

    model_config = ConfigDict(from_attributes=True)
