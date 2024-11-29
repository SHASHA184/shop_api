from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.order import OrderModel
from schemas.orders import OrderCreate, OrderUpdate, Order
from sqlalchemy import select
from app.services.product_service import ProductService
from app.services.base_service import BaseService


class OrderService(BaseService):
    def __init__(self, db: Session):
        super().__init__(db)
        self.product_service = ProductService(db)

    async def get(self, skip: int = 0, limit: int = 10):
        query = select(OrderModel).offset(skip).limit(limit)
        db_order = await self.db.execute(query)
        return db_order.scalars().all()

    async def get_one(self, id: int):
        return await self.get_entity_or_404(OrderModel, id)

    async def create(self, obj: OrderCreate):
        product = await self.product_service.get_one(obj.product_id)
        if product.quantity < obj.quantity:
            raise HTTPException(status_code=400, detail="Insufficient stock")
        product.quantity -= obj.quantity
        await product.update(self.db)
        db_order = OrderModel(**obj.dict())
        await db_order.save(self.db)
        return db_order

    async def update(self, id: int, obj: OrderUpdate):
        db_order = await self.get_one(id)
        product = await self.product_service.get_one(db_order.product_id)
        if obj.quantity:
            if product.quantity < obj.quantity:
                raise HTTPException(status_code=400, detail="Insufficient stock")
            if db_order.quantity < obj.quantity:
                product.quantity -= obj.quantity - db_order.quantity
            else:
                product.quantity += db_order.quantity - obj.quantity
            await product.update(self.db)
        await db_order.update(self.db, **obj.dict(exclude_unset=True))
        return db_order

    async def delete(self, id: int):
        db_order = await self.get_one(id)
        product = await self.product_service.get_one(db_order.product_id)
        product.quantity += db_order.quantity
        await product.update(self.db)
        await db_order.delete(self.db)
        return db_order
