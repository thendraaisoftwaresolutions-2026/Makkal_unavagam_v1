
from uuid import UUID
from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict


class CategoryCreate(BaseModel):
    name_tamil: str = Field(min_length=1, max_length=100)
    name_english: str = Field(min_length=1, max_length=100)
    display_order: int = Field(default=0, ge=0)
    is_active: bool = True


class CategoryResponse(BaseModel):
    id: UUID
    name_tamil: str
    name_english: str
    display_order: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class CategoryUpdate(CategoryCreate):
    pass


class MenuItemCreate(BaseModel):
    category_id: UUID
    name_tamil: str = Field(min_length=1, max_length=150)
    name_english: str = Field(min_length=1, max_length=150)
    price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    image_url: str | None = None
    is_available: bool = True


class MenuItemResponse(BaseModel):
    id: UUID
    category_id: UUID
    name_tamil: str
    name_english: str
    price: Decimal
    image_url: str | None
    is_available: bool

    model_config = ConfigDict(from_attributes=True)


class MenuItemUpdate(MenuItemCreate):
    pass


class MenuAvailabilityUpdate(BaseModel):
    is_available: bool
