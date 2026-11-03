
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID


class DeviceCreate(BaseModel):
    device_name: str = Field(min_length=2, max_length=100)
    device_type: str = Field(min_length=2, max_length=50)


class DeviceResponse(BaseModel):
    device_id: UUID = Field(
        validation_alias="id",
        serialization_alias="device_id",
    )
    device_name: str
    device_type: str
    is_active: bool
    last_sync_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class DeviceStatusUpdate(BaseModel):
    is_active: bool
