from fastapi import HTTPException
from sqlalchemy import select
from app.models.reservation import ReservationModel
from app.models.product import ProductModel
from app.schemas.reservations import ReservationCreate, ReservationUpdate
from app.services.base_service import BaseService


class ReservationService(BaseService):
    async def get(self, skip: int = 0, limit: int = 10):
        query = select(ReservationModel).offset(skip).limit(limit)
        db_reservation = await self.db.execute(query)
        return db_reservation.scalars().all()

    async def get_one(self, id: int):
        return await self.get_entity_or_404(ReservationModel, id)

    async def create(self, obj: ReservationCreate):
        product = await self.db.get(ProductModel, obj.product_id)
        if product.quantity < obj.quantity:
            raise HTTPException(status_code=400, detail="Insufficient stock")
        product.quantity -= obj.quantity
        await product.update(self.db)
        db_reservation = ReservationModel(**obj.dict())
        await db_reservation.save(self.db)
        return db_reservation

    async def update(self, id: int, obj: ReservationUpdate):
        db_reservation = await self.get_one(id)
        product = await self.db.get(ProductModel, db_reservation.product_id)
        if obj.quantity:
            if product.quantity < obj.quantity:
                raise HTTPException(status_code=400, detail="Insufficient stock")
            if db_reservation.quantity < obj.quantity:
                product.quantity -= obj.quantity - db_reservation.quantity
            else:
                product.quantity += db_reservation.quantity - obj.quantity
            await product.update(self.db)
        await db_reservation.update(self.db, **obj.dict(exclude_unset=True))
        return db_reservation

    async def delete(self, id: int):
        db_reservation = await self.get_one(id)
        product = await self.db.get(ProductModel, db_reservation.product_id)
        product.quantity += db_reservation.quantity
        await product.update(self.db)
        await db_reservation.delete(self.db)
        return db_reservation
