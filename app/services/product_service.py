from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models import ProductModel
from schemas.products import ProductCreate, ProductUpdate, Product
from sqlalchemy import select, delete
from app.services.base_service import BaseService


class ProductService(BaseService):
    async def get(self, skip: int = 0, limit: int = 10):
        cache_key = self.get_cache_key(is_list=True, skip=skip, limit=limit)

        cached_products = await self.redis_service.get_json(cache_key)

        if cached_products:
            return cached_products

        query = select(ProductModel).offset(skip).limit(limit)
        db_product = await self.db.execute(query)
        products = db_product.scalars().all()

        await self.redis_service.set_json(
            cache_key,
            [Product.model_validate(product).model_dump_json() for product in products],
        )
        return products

    async def get_one(self, id: int, use_cache=True):
        cache_key = self.get_cache_key(id=id)
        if use_cache:
            cached_product = await self.redis_service.get_json(cache_key)

            if cached_product:
                return cached_product

        product = await self.get_entity_or_404(ProductModel, id)
        await self.redis_service.set_json(
            cache_key, Product.model_validate(product).model_dump_json()
        )
        return product

    async def create(self, obj: ProductCreate):
        db_product = ProductModel(**obj.model_dump())
        await db_product.save(self.db)

        cache_key = self.get_cache_key(id=db_product.id)
        await self.redis_service.set_json(
            cache_key,
            Product.model_validate(db_product).model_dump_json(),
        )

        await self.invalidate_list_cache()

        return db_product

    async def update(self, id: int, obj: ProductUpdate):
        db_product = await self.get_one(id, use_cache=False)
        await db_product.update(self.db, **obj.dict(exclude_unset=True))

        updated_product = Product.model_validate(db_product).model_dump_json()
        cache_key = self.get_cache_key(id=id)
        await self.redis_service.set_json(cache_key, updated_product)

        await self.invalidate_list_cache()

        return db_product

    async def delete(self, id: int):
        product = await self.get_one(id, use_cache=False)
        await product.delete(self.db)

        await self.invalidate_entity_cache(id)
        await self.invalidate_list_cache()

        return product
