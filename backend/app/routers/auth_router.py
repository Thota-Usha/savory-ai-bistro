import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import (
    UserRegister, UserLogin, UserUpdate, PasswordUpdate, 
    UserResponse, TokenResponse, FirebaseLoginRequest
)
from app.auth import hash_password, verify_password, create_access_token, get_current_user
from app.services.firebase_service import firebase_service

router = APIRouter(prefix="/auth", tags=["Authentication"])

def format_user_response(user: User) -> UserResponse:
    prefs = []
    if user.dietary_preferences:
        try:
            prefs = json.loads(user.dietary_preferences)
        except Exception:
            prefs = []
    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        role=user.role,
        phone=user.phone,
        address=user.address,
        dietary_preferences=prefs,
        firebase_uid=user.firebase_uid
    )

@router.post("/register", response_model=TokenResponse)
def register(data: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == data.email.lower()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists"
        )
    
    try:
        user = User(
            name=data.name.strip(),
            email=data.email.lower().strip(),
            hashed_password=hash_password(data.password),
            role="customer",
            phone=data.phone,
            address=data.address,
            dietary_preferences=json.dumps(data.dietary_preferences or [])
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {str(exc)}"
        )

    token = create_access_token({"sub": user.id, "email": user.email, "role": user.role})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=format_user_response(user)
    )

@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email.lower().strip()).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password credentials"
        )

    token = create_access_token({"sub": user.id, "email": user.email, "role": user.role})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=format_user_response(user)
    )

@router.post("/firebase-login", response_model=TokenResponse)
def firebase_login(data: FirebaseLoginRequest, db: Session = Depends(get_db)):
    """Verifies Firebase ID token, finds or creates the user account, and returns authenticated JWT."""
    try:
        fb_user = firebase_service.verify_firebase_token(data.id_token)
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(ve)
        )

    fb_uid = fb_user.get("uid")
    email = (fb_user.get("email") or data.email or f"{fb_uid}@firebase.user").lower().strip()
    name = fb_user.get("name") or data.name or "Savory Patron"
    phone = fb_user.get("phone") or data.phone

    # Search existing user by firebase_uid or email
    user = db.query(User).filter((User.firebase_uid == fb_uid) | (User.email == email)).first()

    if not user:
        user = User(
            name=name,
            email=email,
            hashed_password=hash_password(f"firebase-oauth-{fb_uid}"),
            role="customer",
            phone=phone,
            firebase_uid=fb_uid,
            dietary_preferences="[]"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # Link UID if not present
        if not user.firebase_uid:
            user.firebase_uid = fb_uid
            db.commit()
            db.refresh(user)

    token = create_access_token({"sub": user.id, "email": user.email, "role": user.role})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=format_user_response(user)
    )

@router.get("/me", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    return format_user_response(current_user)

@router.put("/profile", response_model=UserResponse)
def update_profile(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if data.name is not None:
        current_user.name = data.name.strip()
    if data.phone is not None:
        current_user.phone = data.phone.strip()
    if data.address is not None:
        current_user.address = data.address.strip()
    if data.dietary_preferences is not None:
        current_user.dietary_preferences = json.dumps(data.dietary_preferences)

    db.commit()
    db.refresh(current_user)
    return format_user_response(current_user)

@router.put("/change-password")
def change_password(
    data: PasswordUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    current_user.hashed_password = hash_password(data.new_password)
    db.commit()
    return {"message": "Password updated successfully"}
