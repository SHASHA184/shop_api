from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models import ProductModel
from schemas.products import ProductCreate, ProductUpdate, Product
from sqlalchemy import select

class ProductService:
    def __init__(self, db: Session):
        self.db = db

    async def get_products(self, skip: int = 0, limit: int = 100):
        query = select(ProductModel).offset(skip).limit(limit)
        db_product = await self.db.execute(query)
        return db_product.scalars().all()

    async def get_product(self, product_id: int):
        query = select(ProductModel).filter(ProductModel.id == product_id)
        db_product = await self.db.execute(query)
        db_product = db_product.scalars().first()
        if db_product is None:
            raise HTTPException(status_code=404, detail="ProductModel not found")
        return db_product

    async def create_product(self, product: ProductCreate):
        db_product = ProductModel(**product.dict())
        await db_product.save(self.db)
        return db_product

    async def update_product(self, product_id: int, ProductModel: ProductUpdate):
        db_product = await self.get_product(product_id)
        await db_product.update(self.db, **ProductModel.dict(exclude_unset=True))
        return db_product

    async def delete_product(self, product_id: int):
        db_product = await self.get_product(product_id)
        if db_product is None:
            raise HTTPException(status_code=404, detail="ProductModel not found")
        await db_product.delete(self.db)
        return db_product