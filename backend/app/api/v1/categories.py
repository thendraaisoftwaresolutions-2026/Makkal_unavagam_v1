
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.menu import Category
from app.models.user import User
from app.schemas.menu import CategoryCreate, CategoryUpdate, CategoryResponse
from app.api.v1.dependencies import get_current_user
from app.api.v1.permissions import require_admin

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post("/", response_model=CategoryResponse)
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    category = Category(**data.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.get("/", response_model=list[CategoryResponse])
def list_categories(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return db.scalars(
        select(Category).order_by(Category.display_order)
    ).all()


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: UUID,
    data: CategoryUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    category = db.get(Category, category_id)

    if not category:
        raise HTTPException(404, "Category not found")

    for field, value in data.model_dump().items():
        setattr(category, field, value)

    db.commit()
    db.refresh(category)
    return category
