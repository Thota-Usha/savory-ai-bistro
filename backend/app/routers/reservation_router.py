from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Reservation, User
from app.schemas import ReservationCreate, ReservationResponse
from app.auth import get_optional_current_user, get_current_user
from app.services.firebase_service import firebase_service

router = APIRouter(prefix="/reservations", tags=["Table Reservations"])

@router.post("", response_model=ReservationResponse, status_code=status.HTTP_201_CREATED)
def create_reservation(
    data: ReservationCreate,
    user: User = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    reservation = Reservation(
        user_id=user.id if user else None,
        name=data.name.strip(),
        email=data.email.strip().lower(),
        phone=data.phone.strip(),
        date=data.date.strip(),
        time=data.time.strip(),
        guests=data.guests,
        area=data.area.strip(),
        special_requests=data.special_requests.strip() if data.special_requests else None,
        status="confirmed"
    )
    db.add(reservation)
    db.commit()
    db.refresh(reservation)

    resp = ReservationResponse(
        id=reservation.id,
        user_id=reservation.user_id,
        name=reservation.name,
        email=reservation.email,
        phone=reservation.phone,
        date=reservation.date,
        time=reservation.time,
        guests=reservation.guests,
        area=reservation.area,
        special_requests=reservation.special_requests,
        status=reservation.status,
        created_at=reservation.created_at.isoformat() if reservation.created_at else None
    )

    try:
        firebase_service.sync_reservation_to_firestore(resp.dict())
    except Exception:
        pass

    return resp

@router.get("/my-reservations", response_model=List[ReservationResponse])
def get_user_reservations(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    res_list = db.query(Reservation).filter(Reservation.user_id == user.id).order_by(Reservation.created_at.desc()).all()
    return [
        ReservationResponse(
            id=r.id,
            user_id=r.user_id,
            name=r.name,
            email=r.email,
            phone=r.phone,
            date=r.date,
            time=r.time,
            guests=r.guests,
            area=r.area,
            special_requests=r.special_requests,
            status=r.status,
            created_at=r.created_at.isoformat() if r.created_at else None
        )
        for r in res_list
    ]
