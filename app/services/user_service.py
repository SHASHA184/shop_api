from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.utils import hash_password, verify_password
from app.models.user import UserModel
from app.schemas.users import UserCreate, UserUpdate, User
from sqlalchemy.sql.expression import select
from app.services.base_service import BaseService


class UserService(BaseService):
    async def get(self, skip: int = 0, limit: int = 10):
        query = select(UserModel).offset(skip).limit(limit)
        users = await self.db.execute(query)
        return users.scalars().all()
    
    async def get_one(self, id: int):
        return await self.get_entity_or_404(UserModel, id)
    
    async def create(self, obj: UserCreate):
        db_user = UserModel(**obj.dict())
        db_user.password = hash_password(db_user.password)
        await db_user.save(self.db)
        return db_user
    
    async def update(self, id: int, obj: UserUpdate):
        db_user = await self.get_one(id)
        if obj.password:
            obj.password = hash_password(obj.password)
        await db_user.update(self.db, **obj.dict(exclude_unset=True))
        return db_user
    
    async def delete(self, id: int):
        user = await self.get_one(id)
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