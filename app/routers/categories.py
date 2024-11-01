from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.database import get_db
from schemas.categories import CategoryCreate, Category
from services.category_service import CategoryService

router = APIRouter()


@router.get("/categories/{category_id}", response_model=Category)
async def read_category(category_id: int, db: Session = Depends(get_db)):
    service = CategoryService(db)
    return await service.get_category(category_id)


@router.post("/categories/", response_model=Category)
async def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    service = CategoryService(db)
    return await service.create_category(category)


@router.get("/categories/", response_model=list[Category])
async def read_categories(
    skip: int = 0, limit: int = 10, db: Session = Depends(get_db)
):
    service = CategoryService(db)
    return await service.get_categories(skip=skip, limit=limit)


@router.put("/categories/{category_id}", response_model=Category)
async def update_category(
    category_id: int, category: CategoryCreate, db: Session = Depends(get_db)
):
    service = CategoryService(db)
    return await service.update_category(category_id, category)


@router.delete("/categories/{category_id}", response_model=Category)
async def delete_category(category_id: int, db: Session = Depends(get_db)):
    service = CategoryService(db)
    return await service.delete_category(category_id)