from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Inquiry
from app.schemas import InquiryCreate, InquiryResponse
from app.services.integrity_service import validate_inquiry_integrity

router = APIRouter(prefix="/contact", tags=["Contact & Inquiries"])

@router.post("", response_model=InquiryResponse, status_code=status.HTTP_201_CREATED)
def submit_contact_inquiry(
    data: InquiryCreate,
    db: Session = Depends(get_db)
):
    integrity = validate_inquiry_integrity(data.email, data.subject, data.message, db)
    if not integrity["passed"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contact message failed security or formatting integrity checks"
        )

    inquiry = Inquiry(
        name=data.name.strip(),
        email=data.email.strip().lower(),
        phone=data.phone.strip() if data.phone else None,
        subject=data.subject.strip(),
        message=data.message.strip(),
        integrity_status=integrity["integrity_status"],
        status="unread"
    )
    try:
        db.add(inquiry)
        db.commit()
        db.refresh(inquiry)
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to submit message: {str(exc)}"
        )

    return InquiryResponse(
        id=inquiry.id,
        name=inquiry.name,
        email=inquiry.email,
        phone=inquiry.phone,
        subject=inquiry.subject,
        message=inquiry.message,
        integrity_status=inquiry.integrity_status,
        status=inquiry.status,
        created_at=inquiry.created_at.isoformat() if inquiry.created_at else None
    )
