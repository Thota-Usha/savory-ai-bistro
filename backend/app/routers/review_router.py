from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Review, User
from app.schemas import ReviewCreate, ReviewResponse
from app.auth import get_optional_current_user
from app.services.integrity_service import validate_review_integrity

router = APIRouter(prefix="/reviews", tags=["Reviews & Testimonials"])

@router.get("", response_model=List[ReviewResponse])
def get_reviews(db: Session = Depends(get_db)):
    reviews = db.query(Review).filter(Review.is_flagged == False).order_by(Review.created_at.desc()).all()
    return [
        ReviewResponse(
            id=r.id,
            user_name=r.user_name,
            user_avatar=r.user_avatar,
            rating=r.rating,
            dish_name=r.dish_name,
            comment=r.comment,
            sentiment=r.sentiment,
            verified_order=r.verified_order,
            integrity_score=r.integrity_score,
            is_flagged=r.is_flagged,
            created_at=r.created_at.isoformat() if r.created_at else None
        )
        for r in reviews
    ]

@router.post("", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def submit_review(
    data: ReviewCreate,
    user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    # AI Sentiment & Integrity moderation check
    integrity = validate_review_integrity(data.comment, data.rating, db)
    if integrity["is_flagged"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Review Content Integrity Violation: {integrity['flag_reason']}"
        )

    user_name = user.name if user else "Gourmet Guest"
    avatar = "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?auto=format&fit=crop&w=150&q=80"

    review = Review(
        user_id=user.id if user else None,
        user_name=user_name,
        user_avatar=avatar,
        rating=data.rating,
        dish_name=data.dish_name or "Chef's Tasting Experience",
        comment=data.comment.strip(),
        sentiment=integrity["sentiment"],
        verified_order=bool(user),
        integrity_score=integrity["integrity_score"],
        is_flagged=integrity["is_flagged"]
    )
    db.add(review)
    db.commit()
    db.refresh(review)

    return ReviewResponse(
        id=review.id,
        user_name=review.user_name,
        user_avatar=review.user_avatar,
        rating=review.rating,
        dish_name=review.dish_name,
        comment=review.comment,
        sentiment=review.sentiment,
        verified_order=review.verified_order,
        integrity_score=review.integrity_score,
        is_flagged=review.is_flagged,
        created_at=review.created_at.isoformat() if review.created_at else None
    )
