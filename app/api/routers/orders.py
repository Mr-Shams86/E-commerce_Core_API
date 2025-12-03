from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.api.services.orders import create_order_for_user, get_orders_for_user
from app.models import User
from app.schemas.order import OrderCreate, OrderRead

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post(
    "",
    response_model=OrderRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create an order for current user",
)
def create_order(
    payload: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> OrderRead:
    order = create_order_for_user(db, current_user.id, payload)
    return order


@router.get(
    "/me",
    response_model=List[OrderRead],
    summary="List orders of current user",
)
def list_my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[OrderRead]:
    orders = get_orders_for_user(db, current_user.id)
    return orders
