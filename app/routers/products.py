from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.product import Product
from app.schemas.products import ProductCreate, ProductUpdate
from app.services.product_service import ProductService

router = APIRouter()


@router.post("/products/", response_model=Product)
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    service = ProductService(db)
    return await service.create_product(product)


@router.get("/products/", response_model=list[Product])
async def read_products(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    service = ProductService(db)
    return await service.get_products(skip=skip, limit=limit)


@router.put("/products/{product_id}", response_model=Product)
async def update_product(
    product_id: int, product: ProductUpdate, db: Session = Depends(get_db)
):
    service = ProductService(db)
    return await service.update_product(product_id, product)


@router.delete("/products/{product_id}", response_model=Product)
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    service = ProductService(db)
    return await service.delete_product(product_id)
