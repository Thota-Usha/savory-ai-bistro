from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Coupon
from app.schemas import (
    AIChatRequest, AIChatResponse,
    AIRecommendationRequest, AIMenuGenRequest,
    CouponValidateRequest
)
from app.auth import get_optional_current_user, require_admin
from app.services.ai_service import (
    chat_with_sommelier,
    get_personalized_recommendations,
    generate_menu_item_ai
)
from app.routers.menu_router import format_menu_item

router = APIRouter(prefix="/ai", tags=["AI Intelligence Engine"])

@router.post("/chat", response_model=AIChatResponse)
async def sommelier_chat(
    data: AIChatRequest,
    user: User = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    result = await chat_with_sommelier(
        user_message=data.message,
        history=data.history or [],
        user=user,
        db=db
    )
    return AIChatResponse(
        reply=result["reply"],
        source=result["source"],
        suggested_dishes=result.get("suggested_dishes", [])
    )

@router.post("/recommendations")
async def personalized_recommendations(
    data: AIRecommendationRequest,
    user: User = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    result = await get_personalized_recommendations(
        mood=data.mood,
        dietary=data.dietary,
        budget=data.budget,
        user=user,
        db=db
    )
    formatted = [format_menu_item(m) for m in result["recommendations"]]
    return {
        "recommendations": formatted,
        "explanation": result["explanation"],
        "confidence_score": result["confidence_score"]
    }

@router.post("/generate-menu-item")
async def generate_menu_item(
    data: AIMenuGenRequest,
    admin: User = Depends(require_admin)
):
    dish_data = await generate_menu_item_ai(data.concept)
    return dish_data

@router.post("/validate-coupon")
def validate_coupon(
    data: CouponValidateRequest,
    db: Session = Depends(get_db)
):
    coupon = db.query(Coupon).filter(
        Coupon.code == data.code.strip().upper(),
        Coupon.is_active == True
    ).first()

    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Promo code '{data.code}' is invalid or has expired."
        )

    if data.subtotal < coupon.min_order:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Promo code '{coupon.code}' requires a minimum order subtotal of ${coupon.min_order:.2f}."
        )

    discount = min(data.subtotal * (coupon.discount_percent / 100.0), coupon.max_discount)
    return {
        "code": coupon.code,
        "discount_percent": coupon.discount_percent,
        "discount_amount": round(discount, 2),
        "description": coupon.description
    }
