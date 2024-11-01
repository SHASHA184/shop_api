from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemas.users import UserCreate, UserUpdate, UserView
from app.services.user_service import UserService

router = APIRouter()


@router.get("/users/{user_id}", response_model=UserView)
async def read_user(user_id: int, db: Session = Depends(get_db)):
    service = UserService(db)
    return await service.get_user(user_id)


@router.post("/users/", response_model=UserView)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    service = UserService(db)
    return await service.create_user(user)


@router.get("/users/", response_model=list[UserView])
async def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    service = UserService(db)
    return await service.get_users(skip=skip, limit=limit)


@router.put("/users/{user_id}", response_model=UserView)
async def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    service = UserService(db)
    return await service.update_user(user_id, user)


@router.delete("/users/{user_id}", response_model=UserView)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    service = UserService(db)
    return await service.delete_user(user_id)
