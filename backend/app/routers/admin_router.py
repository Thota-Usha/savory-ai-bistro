import json
import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import Order, Reservation, Review, Inquiry, IntegrityLog, MenuItem, User
from app.schemas import OrderResponse, ReservationResponse, InquiryResponse, OrderStatusUpdate
from app.auth import require_admin
from app.routers.order_router import format_order_response

router = APIRouter(prefix="/admin", tags=["Admin Dashboard"])

@router.get("/analytics")
def get_admin_analytics(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    orders = db.query(Order).all()
    total_revenue = sum(o.total for o in orders if o.status != "cancelled")
    total_orders = len(orders)
    active_orders = sum(1 for o in orders if o.status in ["pending", "preparing", "quality_check", "out_for_delivery"])
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0.0

    reservations_count = db.query(Reservation).count()
    reviews = db.query(Review).all()
    avg_rating = sum(r.rating for r in reviews) / len(reviews) if reviews else 5.0

    # Integrity metrics
    integrity_logs = db.query(IntegrityLog).all()
    flagged_events = sum(1 for l in integrity_logs if l.status in ["warning", "blocked"])

    return {
        "total_revenue": round(total_revenue, 2),
        "total_orders": total_orders,
        "active_orders": active_orders,
        "average_order_value": round(avg_order_value, 2),
        "total_reservations": reservations_count,
        "average_rating": round(avg_rating, 1),
        "total_reviews": len(reviews),
        "integrity_events_total": len(integrity_logs),
        "integrity_flags": flagged_events
    }

@router.get("/orders", response_model=List[OrderResponse])
def get_all_orders(
    status_filter: Optional[str] = Query(None, alias="status"),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    query = db.query(Order)
    if status_filter and status_filter != "all":
        query = query.filter(Order.status == status_filter)
    orders = query.order_by(Order.created_at.desc()).all()
    return [format_order_response(o) for o in orders]

@router.put("/orders/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: str,
    data: OrderStatusUpdate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = data.status
    now_iso = datetime.datetime.utcnow().isoformat() + "Z"

    timeline_map = {
        "pending": "Order confirmed by restaurant.",
        "preparing": "Executive Chef Alessandro and culinary team are preparing your dishes.",
        "quality_check": "Culinary inspection passed. Dish temperature and allergen integrity verified.",
        "out_for_delivery": "Handed off to private courier. In transit to your address.",
        "delivered": "Successfully delivered. Bon appétit!",
        "cancelled": "Order was cancelled by restaurant administration."
    }

    detail_msg = data.note or timeline_map.get(data.status, f"Status updated to {data.status}")

    timeline = []
    if order.tracking_timeline:
        try:
            timeline = json.loads(order.tracking_timeline)
        except Exception:
            timeline = []

    timeline.append({
        "status": data.status.replace("_", " ").title(),
        "timestamp": now_iso,
        "detail": detail_msg
    })
    order.tracking_timeline = json.dumps(timeline)

    db.commit()
    db.refresh(order)
    return format_order_response(order)

@router.get("/reservations", response_model=List[ReservationResponse])
def get_all_reservations(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    res_list = db.query(Reservation).order_by(Reservation.date.desc(), Reservation.time.desc()).all()
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

@router.put("/reservations/{res_id}/status")
def update_reservation_status(
    res_id: str,
    status_str: str = Query(..., alias="status"),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    res = db.query(Reservation).filter(Reservation.id == res_id).first()
    if not res:
        raise HTTPException(status_code=404, detail="Reservation not found")
    res.status = status_str
    db.commit()
    return {"message": f"Reservation updated to {status_str}"}

@router.get("/integrity-logs")
def get_integrity_logs(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    logs = db.query(IntegrityLog).order_by(IntegrityLog.timestamp.desc()).limit(100).all()
    result = []
    for l in logs:
        det = {}
        if l.details:
            try:
                det = json.loads(l.details)
            except Exception:
                det = {"raw": l.details}
        result.append({
            "id": l.id,
            "timestamp": l.timestamp.isoformat() if l.timestamp else None,
            "event_type": l.event_type,
            "severity": l.severity,
            "details": det,
            "status": l.status
        })
    return result

@router.get("/inquiries", response_model=List[InquiryResponse])
def get_all_inquiries(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    inquiries = db.query(Inquiry).order_by(Inquiry.created_at.desc()).all()
    return [
        InquiryResponse(
            id=i.id,
            name=i.name,
            email=i.email,
            phone=i.phone,
            subject=i.subject,
            message=i.message,
            integrity_status=i.integrity_status,
            status=i.status,
            created_at=i.created_at.isoformat() if i.created_at else None
        )
        for i in inquiries
    ]
