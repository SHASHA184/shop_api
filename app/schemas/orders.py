from pydantic import BaseModel
from typing import Optional
from typing import List


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int


class OrderItem(OrderItemCreate):
    id: int
    price_at_order_time: float

    class Config:
        orm_mode = True
        from_attributes = True


class OrderUpdate(BaseModel):
    items: Optional[List[OrderItemCreate]] = None


class OrderCreate(BaseModel):
    user_id: int
    items: List[OrderItemCreate]


class Order(BaseModel):
    id: int
    user_id: int
    items: List[OrderItem]

    class Config:
        orm_mode = True
        from_attributes = True
