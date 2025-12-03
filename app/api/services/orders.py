from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.catalog import Inventory, Product
from app.models.order import Order, OrderItem, OrderStatus
from app.schemas.order import OrderCreate


def create_order_for_user(
    db: Session,
    user_id: int,
    order_in: OrderCreate,
) -> Order:
    if not order_in.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order must contain at least one item.",
        )
    product_ids = {item.product_id for item in order_in.items}

    # Validate products and inventories
    products = db.query(Product).filter(Product.id.in_(product_ids), Product.is_active.is_(True)).all()
    products_by_id = {p.id: p for p in products}

    # Fetch inventories for products that track inventory
    inventories = (
        db.query(Inventory)
        .filter(
            Inventory.product_id.in_(product_ids),
            Inventory.track_inventory.is_(True),
        )
        .all()
    )
    inv_by_pid = {inv.product_id: inv for inv in inventories}

    total_cents = 0
    order_items: list[OrderItem] = []

    # Validate items and prepare order items
    for item in order_in.items:
        product = products_by_id.get(item.product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product {item.product_id} not found or inactive.",
            )

        inv = inv_by_pid.get(item.product_id)
        if inv and inv.qty < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Not enough stock for product {item.product_id}.",
            )

        # Update inventory
        if inv:
            inv.qty -= item.quantity

        line_total = product.price_cents * item.quantity
        total_cents += line_total

        order_items.append(
            OrderItem(
                product_id=product.id,
                quantity=item.quantity,
                price_cents=product.price_cents,
            )
        )

    order = Order(
        user_id=user_id,
        status=OrderStatus.NEW,
        total_cents=total_cents,
        items=order_items,
    )

    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def get_orders_for_user(db: Session, user_id: int) -> list[Order]:
    return db.query(Order).filter(Order.user_id == user_id).order_by(Order.created_at.desc()).all()
