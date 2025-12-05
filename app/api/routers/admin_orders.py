from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_superuser
from app.models.order import Order, OrderStatus
from app.schemas.order import AdminOrderRead, AdminOrderUpdate

router = APIRouter(
    prefix="/admin/orders",
    tags=["admin:orders"],
)


@router.get(
    "",
    response_model=List[AdminOrderRead],
    summary="List all orders (admin)",
)
def list_orders(
    status: Optional[OrderStatus] = Query(default=None),
    user_id: Optional[int] = Query(default=None),
    db: Session = Depends(get_db),
    current_admin=Depends(require_superuser),
) -> list[AdminOrderRead]:
    """
    List orders with optional filters:
    - by status
    - by user_id
    """
    query = db.query(Order)

    if status is not None:
        query = query.filter(Order.status == status)

    if user_id is not None:
        query = query.filter(Order.user_id == user_id)

    query = query.order_by(Order.created_at.desc())

    return list(query.all())


@router.patch(
    "/{order_id}",
    response_model=AdminOrderRead,
    summary="Update order status (admin)",
)
def update_order_status(
    order_id: int,
    payload: AdminOrderUpdate,
    db: Session = Depends(get_db),
    current_admin=Depends(require_superuser),
) -> AdminOrderRead:
    from fastapi import HTTPException, status

    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found.",
        )

    order.status = payload.status

    db.add(order)
    db.commit()
    db.refresh(order)

    return order
