from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemas.users import UserView
from app.services.user_service import UserService
from app.auth import get_current_user
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()


@router.post("/auth/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    service = UserService(db)
    return await service.login(form_data.username, form_data.password)


@router.get("/auth/me", response_model=UserView)
async def get_me(current_user: dict = Depends(get_current_user)):
    return current_user
