from pydantic import BaseModel, EmailStr
from typing import Optional


class UserView(BaseModel):
    id: int
    username: str
    email: EmailStr


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class User(UserCreate):
    id: int

    class Config:
        orm_mode = True
