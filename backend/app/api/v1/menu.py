
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.menu import MenuItem, Category
from app.models.user import User
from app.schemas.menu import (
    MenuItemCreate,
    MenuItemUpdate,
    MenuItemResponse,
    MenuAvailabilityUpdate,
)
from app.api.v1.dependencies import get_current_user
from app.api.v1.permissions import require_admin

router = APIRouter(prefix="/menu", tags=["Menu Management"])


@router.post("/", response_model=MenuItemResponse)
def create_menu_item(
    data: MenuItemCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    category = db.get(Category, data.category_id)

    if not category or not category.is_active:
        raise HTTPException(
            status_code=400,
            detail="Category does not exist or is inactive",
        )

    item = MenuItem(**data.model_dump())

    db.add(item)
    db.commit()
    db.refresh(item)

    return item


@router.get("/", response_model=list[MenuItemResponse])
def list_menu_items(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return db.scalars(
        select(MenuItem).order_by(MenuItem.name_english)
    ).all()


@router.put("/{item_id}", response_model=MenuItemResponse)
def update_menu_item(
    item_id: UUID,
    data: MenuItemUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    item = db.get(MenuItem, item_id)

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Menu item not found",
        )

    category = db.get(Category, data.category_id)

    if not category or not category.is_active:
        raise HTTPException(
            status_code=400,
            detail="Category does not exist or is inactive",
        )

    for field, value in data.model_dump().items():
        setattr(item, field, value)

    db.commit()
    db.refresh(item)

    return item


@router.patch("/{item_id}/availability", response_model=MenuItemResponse)
def update_menu_availability(
    item_id: UUID,
    data: MenuAvailabilityUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    item = db.get(MenuItem, item_id)

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Menu item not found",
        )

    item.is_available = data.is_available

    db.commit()
    db.refresh(item)

    return item
