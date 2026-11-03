
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import select


class RestaurantSettingsUpdate(BaseModel):
    restaurant_name: str = Field(min_length=2, max_length=150)
    phone: str | None = Field(default=None, max_length=30)
    address: str | None = None
    logo_url: str | None = None
    currency: str = Field(default="INR", max_length=10)
    timezone: str = Field(default="Asia/Kolkata", max_length=50)
    receipt_width_mm: int = Field(default=80, ge=58, le=80)


class RestaurantSettingsResponse(RestaurantSettingsUpdate):
    id: str

    model_config = ConfigDict(from_attributes=True)
