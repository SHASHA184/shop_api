from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from schemas.products import ProductCreate, ProductUpdate, Product
from services.product_service import ProductService
import time

router = APIRouter()


@router.post("/products/", response_model=Product)
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    service = ProductService(db)
    return await service.create(product)


@router.get("/products/", response_model=list[Product])
async def read_products(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    start_time = time.monotonic()
    service = ProductService(db)
    result = await service.get(skip=skip, limit=limit)
    print("--- %s seconds ---" % (time.monotonic() - start_time))
    return result


@router.get("/products/{product_id}", response_model=Product)
async def read_product(product_id: int, db: Session = Depends(get_db)):
    start_time = time.monotonic()
    service = ProductService(db)
    result = await service.get_one(product_id)
    print("--- %s seconds ---" % (time.monotonic() - start_time))
    return result


@router.put("/products/{product_id}", response_model=Product)
async def update_product(
    product_id: int, product: ProductUpdate, db: Session = Depends(get_db)
):
    service = ProductService(db)
    return await service.update(product_id, product)


@router.delete("/products/{product_id}", response_model=Product)
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    service = ProductService(db)
    return await service.delete(product_id)
