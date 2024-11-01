from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.utils import hash_password, verify_password
from app.models.user import UserModel
from app.schemas.users import UserCreate, UserUpdate, User
from sqlalchemy.sql.expression import select


class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    async def get_users(self, skip: int = 0, limit: int = 100):
        query = select(UserModel).offset(skip).limit(limit)
        users = await self.db.execute(query)
        return users.scalars().all()
    
    async def get_user(self, user_id: int):
        query = select(UserModel).filter(UserModel.id == user_id)
        user = await self.db.execute(query)
        user = user.scalars().first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    
    async def create_user(self, user: UserCreate):
        db_user = UserModel(**user.dict())
        db_user.password = hash_password(db_user.password)
        await db_user.save(self.db)
        return db_user
    
    async def update_user(self, user_id: int, user: UserUpdate):
        db_user = await self.get_user(user_id)
        if user.password:
            user.password = hash_password(user.password)
        await db_user.update(self.db, **user.dict(exclude_unset=True))
        return db_user
    
    async def delete_user(self, user_id: int):
        user = await self.get_user(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        await user.delete(self.db)
        return user
    
    async def authenticate_user(self, email: str, password: str):
        query = select(UserModel).filter(UserModel.email == email)
        user = await self.db.execute(query)
        user = user.scalars().first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        if not verify_password(password, user.password):
            raise HTTPException(status_code=400, detail="Invalid password")
        return user