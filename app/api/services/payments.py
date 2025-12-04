from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.order import Order, OrderStatus
from app.models.payment import Payment, PaymentStatus


def pay_order_for_user(
    db: Session,
    user_id: int,
    order_id: int,
) -> Payment:
    order: Order | None = db.query(Order).filter(Order.id == order_id, Order.user_id == user_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found.",
        )

    if order.status != OrderStatus.NEW:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order total must be greater than 0.",
        )

    existing_paid = (
        db.query(Payment)
        .filter(
            Payment.order_id == order.id,
            Payment.status == PaymentStatus.PAID,
        )
        .first()
    )
    if existing_paid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order is already paid.",
        )

    provider = "test"
    provider_payment_id = f"test-{uuid4()}"

    payment = Payment(
        order_id=order.id,
        amount_cents=order.total_cents,
        provider=provider,
        provider_payment_id=provider_payment_id,
        status=PaymentStatus.PAID,
    )

    order.status = OrderStatus.CONFIRMED

    db.add(payment)
    db.commit()
    db.refresh(payment)
    db.refresh(order)

    return payment
