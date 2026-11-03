
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.operations import RestaurantSettings
from app.models.user import User
from app.schemas.settings import (
    RestaurantSettingsUpdate,
    RestaurantSettingsResponse,
)
from app.api.v1.permissions import require_admin

router = APIRouter(prefix="/settings", tags=["Restaurant Settings"])


@router.get("/", response_model=RestaurantSettingsResponse)
def get_settings(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    settings = db.scalar(
        select(RestaurantSettings).limit(1)
    )

    if not settings:
        raise HTTPException(
            status_code=404,
            detail="Restaurant settings not configured",
        )

    return settings



@router.put("/", response_model=RestaurantSettingsResponse)
def update_settings(
    data: RestaurantSettingsUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    try:
        settings = db.scalar(
            select(RestaurantSettings).where(
                RestaurantSettings.settings_key == "default"
            )
        )

        if settings is None:
            settings = RestaurantSettings(
                settings_key="default",
                **data.model_dump(),
            )
            db.add(settings)
        else:
            for field, value in data.model_dump().items():
                setattr(settings, field, value)

        db.commit()
        db.refresh(settings)

        return RestaurantSettingsResponse(
            id=str(settings.id),
            restaurant_name=settings.restaurant_name,
            phone=settings.phone,
            address=settings.address,
            logo_url=settings.logo_url,
            currency=settings.currency,
            timezone=settings.timezone,
            receipt_width_mm=settings.receipt_width_mm,
        )

    except Exception:
        db.rollback()
        raise
