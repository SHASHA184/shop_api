from pydantic import BaseModel
from typing import Optional


class CategoryCreate(BaseModel):
    name: str


class CategoryUpdate(BaseModel):
    name: Optional[str]


class Category(CategoryCreate):
    id: int

    class Config:
        orm_mode = True