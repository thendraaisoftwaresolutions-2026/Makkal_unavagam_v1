
from decimal import Decimal, ROUND_HALF_UP

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from app.database.connection import get_db
from app.models.device import Device
from app.models.menu import MenuItem
from app.models.order import Order, OrderItem
from app.models.user import User
from app.api.v1.dependencies import get_current_user
from app.api.v1.permissions import require_admin_or_cashier
from app.schemas.order import OrderCreate, OrderResponse
from uuid import UUID
from fastapi import Query
from app.models.order import OrderStatus
from app.schemas.order_status import OrderStatusUpdate



router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)


@router.post(
    "/",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_order(
    data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_cashier),
):
    # Validate device
    device = db.scalar(
        select(Device).where(
            Device.id == data.device_id,
            Device.is_active.is_(True),
        )
    )

    if device is None:
        raise HTTPException(
            status_code=400,
            detail="Device not found or inactive",
        )

    # Reject duplicate menu items in one order
    menu_item_ids = [item.menu_item_id for item in data.items]

    if len(menu_item_ids) != len(set(menu_item_ids)):
        raise HTTPException(
            status_code=400,
            detail="Duplicate menu items are not allowed",
        )

    try:
        # Fetch all menu items from the database
        menu_items = db.scalars(
            select(MenuItem).where(
                MenuItem.id.in_(menu_item_ids)
            )
        ).all()

        menu_item_map = {
            item.id: item for item in menu_items
        }

        # Validate every requested item
        if len(menu_item_map) != len(menu_item_ids):
            raise HTTPException(
                status_code=400,
                detail="One or more menu items do not exist",
            )

        for menu_item in menu_items:
            if not menu_item.is_available:
                raise HTTPException(
                    status_code=400,
                    detail=f"{menu_item.name_english} is unavailable",
                )

            if not menu_item.category.is_active:
                raise HTTPException(
                    status_code=400,
                    detail=f"{menu_item.name_english} belongs to an inactive category",
                )

        # Create the order
        order = Order(
            created_by_user_id=current_user.id,
            device_id=device.id,
            customer_name=data.customer_name,
            customer_phone=data.customer_phone,
            customer_location=data.customer_location,
            notes=data.notes,
        )

        db.add(order)
        db.flush()

        # Create order items using database prices
        for requested_item in data.items:
            menu_item = menu_item_map[requested_item.menu_item_id]

            line_total = (
                menu_item.price * requested_item.quantity
            ).quantize(
                Decimal("0.01"),
                rounding=ROUND_HALF_UP,
            )

            order_item = OrderItem(
                order_id=order.id,
                menu_item_id=menu_item.id,
                item_name_tamil=menu_item.name_tamil,
                item_name_english=menu_item.name_english,
                quantity=requested_item.quantity,
                unit_price=menu_item.price,
                line_total=line_total,
            )

            db.add(order_item)

        db.commit()

        # Reload order with its items
        saved_order = db.scalar(
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.id == order.id)
        )

        return saved_order

    except HTTPException:
        db.rollback()
        raise

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to create order. Please try again.",
        )


@router.get("/", response_model=list[OrderResponse])
def list_orders(
    order_status: OrderStatus | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_cashier),
):
    query = (
        select(Order)
        .options(selectinload(Order.items))
        .order_by(Order.ordered_at.desc())
    )

    if order_status is not None:
        query = query.where(Order.status == order_status)

    return db.scalars(query).all()


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_cashier),
):
    order = db.scalar(
        select(Order)
        .options(selectinload(Order.items))
        .where(Order.id == order_id)
    )

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )

    return order


@router.patch("/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: UUID,
    data: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_cashier),
):
    order = db.scalar(
        select(Order)
        .options(selectinload(Order.items))
        .where(Order.id == order_id)
        .with_for_update()
    )

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )

    allowed_transitions = {
        OrderStatus.PENDING: {
            OrderStatus.PREPARING,
            OrderStatus.CANCELLED,
        },
        OrderStatus.PREPARING: {
            OrderStatus.READY,
            OrderStatus.CANCELLED,
        },
        OrderStatus.READY: {
            OrderStatus.COMPLETED,
            OrderStatus.CANCELLED,
        },
        OrderStatus.COMPLETED: set(),
        OrderStatus.CANCELLED: set(),
    }

    if data.status not in allowed_transitions[order.status]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot change order from {order.status.value} to {data.status.value}",
        )

    try:
        order.status = data.status
        order.version += 1

        db.commit()

        updated_order = db.scalar(
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.id == order_id)
        )

        return updated_order

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to update order status",
        )
