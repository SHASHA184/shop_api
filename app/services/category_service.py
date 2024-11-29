from app.models.category import CategoryModel
from schemas.categories import CategoryCreate, CategoryUpdate, Category
from sqlalchemy import select
from app.services.base_service import BaseService


class CategoryService(BaseService):
    async def get(self, skip: int = 0, limit: int = 10):
        query = select(CategoryModel).offset(skip).limit(limit)
        categories = await self.db.execute(query)
        return categories.scalars().all()

    async def get_one(self, id: int):
        return await self.get_entity_or_404(CategoryModel, id)

    async def create(self, obj: CategoryCreate):
        db_category = CategoryModel(**obj.dict())
        await db_category.save(self.db)
        return db_category

    async def update(self, id: int, obj: CategoryUpdate):
        db_category = await self.get_one(id)
        await db_category.update(self.db, **obj.dict(exclude_unset=True))
        return db_category

    async def delete(self, id: int):
        category = await self.get_one(id)
        await category.delete(self.db)
        return category
