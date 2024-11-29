from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions import EntityNotFoundException
from sqlalchemy.future import select
from app.services.redis_service import RedisService


class BaseService(ABC):
    def __init__(self, db: AsyncSession):
        self.db = db
        self.redis_service = RedisService()

    @abstractmethod
    async def get(self, skip: int = 0, limit: int = 10):
        pass

    @abstractmethod
    async def get_one(self, id: int, use_cache=True):
        pass

    async def get_entity_or_404(self, model, id):
        query = select(model).filter(model.id == id)
        entity = await self.db.execute(query)
        entity = entity.scalars().first()
        if entity is None:
            raise EntityNotFoundException(model.__name__)
        return entity

    @abstractmethod
    async def create(self, obj):
        pass

    @abstractmethod
    async def update(self, id: int, obj):
        pass

    @abstractmethod
    async def delete(self, id: int):
        pass
