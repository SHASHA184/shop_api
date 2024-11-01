from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.category import CategoryModel
from schemas.categories import CategoryCreate, CategoryUpdate, Category
from sqlalchemy import select


class CategoryService:
    def __init__(self, db: Session):
        self.db = db

    async def get_categories(self, skip: int = 0, limit: int = 100):
        query = select(CategoryModel).offset(skip).limit(limit)
        categories = await self.db.execute(query)
        return categories.scalars().all()

    async def get_category(self, category_id: int):
        query = select(CategoryModel).filter(CategoryModel.id == category_id)
        category = await self.db.execute(query)
        category = category.scalars().first()
        if category is None:
            raise HTTPException(status_code=404, detail="Category not found")
        return category

    async def create_category(self, category: CategoryCreate):
        db_category = CategoryModel(**category.dict())
        await db_category.save(self.db)
        return db_category

    async def update_category(self, category_id: int, category: CategoryUpdate):
        db_category = await self.get_category(category_id)
        await db_category.update(self.db, **category.dict(exclude_unset=True))
        return db_category

    async def delete_category(self, category_id: int):
        category = await self.get_category(category_id)
        if category is None:
            raise HTTPException(status_code=404, detail="Category not found")
        await category.delete(self.db)
        return category