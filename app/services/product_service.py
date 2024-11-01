from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.product import Product
from app.schemas.products import ProductCreate, ProductUpdate
from sqlalchemy import select

class ProductService:
    def __init__(self, db: Session):
        self.db = db

    async def get_products(self, skip: int = 0, limit: int = 100):
        query = select(Product).offset(skip).limit(limit)
        products = await self.db.execute(query)
        return products.scalars().all()

    async def get_product(self, product_id: int):
        query = select(Product).filter(Product.id == product_id)
        product = await self.db.execute(query).scalars().first()
        if product is None:
            raise HTTPException(status_code=404, detail="Product not found")
        return product

    def create_product(self, product: ProductCreate):
        db_product = Product(**product.dict())
        db_product.save()
        return db_product

    def update_product(self, product_id: int, product: ProductUpdate):
        db_product = self.get_product(product_id)
        update_data = product.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_product, key, value)
        self.db.commit()
        self.db.refresh(db_product)
        return db_product

    def delete_product(self, product_id: int):
        product = self.get_product(product_id) # Використовуємо get_product для отримання продукту та обробки помилки 404
        self.db.delete(product)
        self.db.commit()
        return product