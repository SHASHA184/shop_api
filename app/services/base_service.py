from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions import EntityNotFoundException
from sqlalchemy.future import select
from app.services.redis_service import RedisService


class BaseService(ABC):
    def __init__(self, db: AsyncSession):
        """
        Base service class for CRUD operations.
        Attributes:
            db (AsyncSession): Async SQLAlchemy session.
            redis_service (RedisService): Redis service instance.
            entity_name (str): Name of the entity.
        """
        self.db = db
        self.redis_service = RedisService()
        self.entity_name = self.__class__.__name__.replace("Service", "").lower()

    @abstractmethod
    async def get(self, skip: int = 0, limit: int = 10):
        """
        Get all entities.
        Args:
            skip (int): Number of entities to skip.
            limit (int): Maximum number of entities to return.
        Returns:
            List of SQLAlchemy model instances.
        """
        pass

    @abstractmethod
    async def get_one(self, id: int, use_cache=True):
        """
        Get a single entity by ID.
        Args:
            id (int): Entity ID.
            use_cache (bool): If True, use the cache.
        Returns:
            SQLAlchemy model instance.
        """
        pass

    async def get_entity_or_404(self, model, id):
        """
        Get an entity by ID or raise a 404 error if it doesn't exist.
        Args:
            model: SQLAlchemy model.
            id (int): Entity ID.
        Returns:
            SQLAlchemy model instance.
        Raises:
            EntityNotFoundException: If the entity doesn't exist.
        """
        query = select(model).filter(model.id == id)
        entity = await self.db.execute(query)
        entity = entity.scalars().first()
        if entity is None:
            raise EntityNotFoundException(model.__name__)
        return entity

    def get_cache_key(self, id: int = None, is_list: bool = False, **kwargs) -> str:
        """
        Generate cache key dynamically.
        Args:
            id (int): Entity ID.
            is_list (bool): If True, generate a list cache key.
            kwargs: Additional parameters for list cache key (e.g., pagination).
        Returns:
            str: Redis cache key.
        """
        if is_list:
            list_key_parts = [f"{key}:{value}" for key, value in kwargs.items()]
            return f"{self.entity_name}s:{':'.join(list_key_parts)}"
        return f"{self.entity_name}:{id}"

    @abstractmethod
    async def create(self, obj):
        """Create an entity."""
        pass

    @abstractmethod
    async def update(self, id: int, obj):
        """Update an entity"""
        pass

    @abstractmethod
    async def delete(self, id: int):
        """Delete an entity."""
        pass

    async def invalidate_entity_cache(self, id: int):
        """Invalidate a single entity's cache."""
        cache_key = self.get_cache_key(id=id)
        await self.redis_service.clear_cache_by_key(cache_key)

    async def invalidate_list_cache(self):
        """Invalidate all list caches for the entity."""
        list_pattern = f"{self.entity_name}s:*"
        await self.redis_service.clear_cache_by_pattern(list_pattern)
