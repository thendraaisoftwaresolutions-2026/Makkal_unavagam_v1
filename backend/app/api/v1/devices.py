
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.device import Device
from app.models.user import User
from app.schemas.device import DeviceCreate, DeviceResponse, DeviceStatusUpdate
from app.api.v1.permissions import require_admin
from uuid import UUID
router = APIRouter(prefix="/devices", tags=["Device Management"])


@router.post("/", response_model=DeviceResponse)
def register_device(
    data: DeviceCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    device = Device(
        device_name=data.device_name,
        device_type=data.device_type,
        is_active=True,
    )

    db.add(device)
    db.commit()
    db.refresh(device)
    return device


@router.get("/", response_model=list[DeviceResponse])
def list_devices(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return db.scalars(select(Device).order_by(Device.device_name)).all()


@router.patch("/{device_id}/status", response_model=DeviceResponse)
def update_device_status(
    device_id: UUID,
    data: DeviceStatusUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    device = db.get(Device, device_id)

    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    device.is_active = data.is_active
    db.commit()
    db.refresh(device)
    return device
