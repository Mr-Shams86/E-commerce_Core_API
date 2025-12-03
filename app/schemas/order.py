from datetime import datetime
from typing import List

from pydantic import BaseModel, Field

from app.models.order import OrderStatus


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class OrderCreate(BaseModel):
    items: List[OrderItemCreate]


class OrderItemRead(BaseModel):
    id: int
    product_id: int
    quantity: int
    price_cents: int

    class Config:
        orm_mode = True


class OrderRead(BaseModel):
    id: int
    status: OrderStatus
    total_cents: int
    created_at: datetime

    class Config:
        orm_mode = True
