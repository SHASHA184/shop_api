from pydantic import BaseModel
from typing import Optional

class OrderCreate(BaseModel):
    user_id: int
    product_id: int
    quantity: int


class OrderUpdate(BaseModel):
    user_id: Optional[int] = None
    product_id: Optional[int] = None
    quantity: Optional[int] = None


class Order(OrderCreate):
    id: int

    class Config:
        orm_mode = True