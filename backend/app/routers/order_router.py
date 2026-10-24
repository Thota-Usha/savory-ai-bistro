import datetime
import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Order, OrderItem, User
from app.schemas import OrderCreate, OrderResponse, OrderItemSchema
from app.auth import get_optional_current_user, get_current_user
from app.services.integrity_service import validate_order_integrity
from app.services.firebase_service import firebase_service

router = APIRouter(prefix="/orders", tags=["Orders & Cart"])

def format_order_response(order: Order) -> OrderResponse:
    timeline = []
    if order.tracking_timeline:
        try:
            timeline = json.loads(order.tracking_timeline)
        except Exception:
            timeline = []

    items = [
        OrderItemSchema(
            menu_item_id=oi.menu_item_id,
            item_name=oi.item_name,
            price=oi.price,
            quantity=oi.quantity,
            special_instructions=oi.special_instructions,
            image=oi.image
        )
        for oi in order.items
    ]

    return OrderResponse(
        id=order.id,
        user_id=order.user_id,
        customer_name=order.customer_name,
        customer_email=order.customer_email,
        customer_phone=order.customer_phone,
        delivery_address=order.delivery_address,
        order_type=order.order_type,
        subtotal=order.subtotal,
        tax=order.tax,
        delivery_fee=order.delivery_fee,
        discount=order.discount,
        tip=order.tip,
        total=order.total,
        coupon_code=order.coupon_code,
        payment_method=order.payment_method,
        status=order.status,
        tracking_timeline=timeline,
        items=items,
        created_at=order.created_at.isoformat() if order.created_at else None
    )

@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    data: OrderCreate,
    user: User = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    if not data.items or len(data.items) == 0:
        raise HTTPException(status_code=400, detail="Shopping cart is empty")

    # 1. AI Integrity Check & Price Verification
    check_result = validate_order_integrity(
        items_data=data.items,
        coupon_code=data.coupon_code,
        tip=data.tip or 0.0,
        user=user,
        db=db
    )

    if not check_result["passed"]:
        error_msg = "; ".join(check_result["errors"])
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Order Integrity Violation: {error_msg}"
        )

    # 2. Build initial timeline
    now_iso = datetime.datetime.utcnow().isoformat() + "Z"
    initial_timeline = [
        {
            "status": "Order Placed",
            "timestamp": now_iso,
            "detail": f"Order received. AI verified pricing & allergen security. Payment authorized."
        }
    ]

    # 3. Create persistent Order
    new_order = Order(
        user_id=user.id if user else None,
        customer_name=data.customer_name.strip(),
        customer_email=data.customer_email.strip().lower(),
        customer_phone=data.customer_phone,
        delivery_address=data.delivery_address,
        order_type=data.order_type,
        subtotal=check_result["subtotal"],
        tax=check_result["tax"],
        delivery_fee=check_result["delivery_fee"],
        discount=check_result["discount"],
        tip=check_result["tip"],
        total=check_result["total"],
        coupon_code=check_result["verified_coupon"],
        payment_method=data.payment_method,
        status="pending",
        tracking_timeline=json.dumps(initial_timeline)
    )
    try:
        db.add(new_order)
        db.commit()
        db.refresh(new_order)

        # 4. Save line items
        for item in data.items:
            order_item = OrderItem(
                order_id=new_order.id,
                menu_item_id=item.menu_item_id,
                item_name=item.item_name,
                price=item.price,
                quantity=item.quantity,
                special_instructions=item.special_instructions or "",
                image=item.image
            )
            db.add(order_item)
        db.commit()
        db.refresh(new_order)
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Order placement failed: {str(exc)}"
        )

    resp = format_order_response(new_order)

    # 5. Sync to Cloud Firestore
    try:
        firebase_service.sync_order_to_firestore(resp.dict())
    except Exception:
        pass

    return resp

@router.get("/my-orders", response_model=List[OrderResponse])
def get_user_orders(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    orders = db.query(Order).filter(Order.user_id == user.id).order_by(Order.created_at.desc()).all()
    return [format_order_response(o) for o in orders]

@router.get("/{order_id}", response_model=OrderResponse)
def get_order_by_id(
    order_id: str,
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return format_order_response(order)

@router.patch("/{order_id}/cancel", response_model=OrderResponse)
def cancel_order(
    order_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.user_id != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="Unauthorized to cancel this order")

    if order.status not in ["pending", "received"]:
        raise HTTPException(status_code=400, detail="Cannot cancel an order already in preparation or transit")

    order.status = "cancelled"
    now_iso = datetime.datetime.utcnow().isoformat() + "Z"
    timeline = json.loads(order.tracking_timeline) if order.tracking_timeline else []
    timeline.append({
        "status": "Order Cancelled",
        "timestamp": now_iso,
        "detail": "Order cancelled by customer request. Refund initiated."
    })
    order.tracking_timeline = json.dumps(timeline)

    db.commit()
    db.refresh(order)
    return format_order_response(order)
