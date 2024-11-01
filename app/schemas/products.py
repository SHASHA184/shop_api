from pydantic import BaseModel
from typing import Optional


class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    quantity: int
    category_id: int


class ProductUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    price: Optional[float]
    quantity: Optional[int]
    category_id: Optional[int]


class Product(ProductCreate):
    id: int

    class Config:
        orm_mode = True
