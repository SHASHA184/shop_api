from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ReservationCreate(BaseModel):
    user_id: int
    product_id: int
    quantity: int


class Reservation(ReservationCreate):
    id: int
    expires_at: datetime

    class Config:
        orm_mode = True


class ReservationUpdate(BaseModel):
    quantity: Optional[int] = None