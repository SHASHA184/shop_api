from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.order import OrderModel
from app.schemas.orders import OrderCreate, OrderUpdate, Order
from app.services.order_service import OrderService

router = APIRouter()


@router.get("/orders/", response_model=list[Order])
async def read_orders(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    service = OrderService(db)
    return await service.get(skip=skip, limit=limit)


@router.get("/orders/{order_id}", response_model=Order)
async def read_order(order_id: int, db: Session = Depends(get_db)):
    service = OrderService(db)
    return await service.get_one(order_id)


@router.post("/orders/", response_model=Order)
async def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    service = OrderService(db)
    return await service.create(order)


@router.put("/orders/{order_id}", response_model=Order)
async def update_order(
    order_id: int, order: OrderUpdate, db: Session = Depends(get_db)
):
    service = OrderService(db)
    return await service.update(order_id, order)


@router.delete("/orders/{order_id}", response_model=Order)
async def delete_order(order_id: int, db: Session = Depends(get_db)):
    service = OrderService(db)
    return await service.delete(order_id)