from datetime import datetime

from pydantic import BaseModel

from app.models.payment import PaymentStatus


class PaymentRead(BaseModel):
    id: int
    order_id: int
    amount_cents: int
    provider: str
    provider_payment_id: str
    status: PaymentStatus
    created_at: datetime

    class Config:
        orm_mode = True
