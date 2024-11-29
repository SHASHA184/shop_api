from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.reservation import ReservationModel
from app.schemas.reservations import ReservationCreate, ReservationUpdate, Reservation
from app.services.reservation_service import ReservationService
from typing import List

router = APIRouter()


@router.get("/reservations/", response_model=List[Reservation])
async def read_reservations(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    service = ReservationService(db)
    return await service.get(skip=skip, limit=limit)


@router.get("/reservations/{reservation_id}", response_model=Reservation)
async def read_reservation(reservation_id: int, db: Session = Depends(get_db)):
    service = ReservationService(db)
    return await service.get_one(reservation_id)


@router.post("/reservations/", response_model=Reservation)
async def create_reservation(reservation: ReservationCreate, db: Session = Depends(get_db)):
    service = ReservationService(db)
    return await service.create(reservation)


@router.put("/reservations/{reservation_id}", response_model=Reservation)
async def update_reservation(
    reservation_id: int, reservation: ReservationUpdate, db: Session = Depends(get_db)
):
    service = ReservationService(db)
    return await service.update(reservation_id, reservation)


@router.delete("/reservations/{reservation_id}", response_model=Reservation)
async def delete_reservation(reservation_id: int, db: Session = Depends(get_db)):
    service = ReservationService(db)
    return await service.delete(reservation_id)