from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.utils import hash_password, verify_password
from app.models.user import UserModel
from app.schemas.users import UserCreate, UserUpdate, User
from sqlalchemy.sql.expression import select
from app.services.base_service import BaseService
from app.utils import create_access_token
from fastapi import status
from sqlalchemy.sql import or_


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

    async def authenticate_user(self, identifier: str, password: str):
        """
        Authenticate user using either email or username.
        """
        is_email = "@" in identifier

        query = select(UserModel).where(
            or_(
                UserModel.email == identifier if is_email else False,
                UserModel.username == identifier if not is_email else False,
            )
        )
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()

        if not user or not verify_password(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username/email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user

    async def login(self, identifier: str, password: str):
        """
        Authenticate and return a JWT token.
        """
        user = await self.authenticate_user(identifier, password)
        access_token = create_access_token(data={"sub": str(user.id)})
        return {"access_token": access_token, "token_type": "bearer"}
