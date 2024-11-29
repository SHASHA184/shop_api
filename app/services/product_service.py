from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models import ProductModel
from schemas.products import ProductCreate, ProductUpdate, Product
from sqlalchemy import select, delete
from app.services.base_service import BaseService


class ProductService(BaseService):
    async def get(self, skip: int = 0, limit: int = 10):
        cache_key = f"products:{skip}:{limit}"

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
        if use_cache:
            cached_product = await self.redis_service.get_json(f"product:{id}")

            if cached_product:
                return cached_product[0]

        product = await self.get_entity_or_404(ProductModel, id)
        await self.redis_service.set_json(
            f"product:{id}", Product.model_validate(product).model_dump_json()
        )
        return product

    async def create(self, obj: ProductCreate):
        db_product = ProductModel(**obj.model_dump())
        await db_product.save(self.db)

        await self.redis_service.set_json(
            f"product:{db_product.id}",
            Product.model_validate(db_product).model_dump_json(),
        )

        await self.invalidate_product_list_cache()

        return db_product

    async def update(self, id: int, obj: ProductUpdate):
        db_product = await self.get_one(id, use_cache=False)
        await db_product.update(self.db, **obj.dict(exclude_unset=True))

        updated_product = Product.model_validate(db_product).model_dump_json()
        await self.redis_service.set_json(f"product:{id}", updated_product)

        await self.invalidate_product_list_cache()

        return db_product

    async def delete(self, id: int):
        product = await self.get_one(id, use_cache=False)
        await product.delete(self.db)

        await self.redis_service.clear_cache_by_key(f"product:{id}")
        
        await self.invalidate_product_list_cache()

        return product

    async def invalidate_product_list_cache(self):
        """Invalidate all product list caches."""
        await self.redis_service.clear_cache_by_pattern("products:*")
