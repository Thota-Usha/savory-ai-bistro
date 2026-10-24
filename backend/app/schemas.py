from typing import List, Optional, Any, Dict
from pydantic import BaseModel, EmailStr, Field

# User Schemas
class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)
    phone: Optional[str] = None
    address: Optional[str] = None
    dietary_preferences: Optional[List[str]] = []

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    dietary_preferences: Optional[List[str]] = None

class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6)

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    phone: Optional[str] = None
    address: Optional[str] = None
    dietary_preferences: List[str] = []
    firebase_uid: Optional[str] = None

    class Config:
        from_attributes = True

class FirebaseLoginRequest(BaseModel):
    id_token: str
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# Menu Item Schemas
class MenuItemCreate(BaseModel):
    name: str
    category: str
    description: str
    price: float
    image: str
    tags: Optional[List[str]] = []
    calories: Optional[int] = 500
    prep_time: Optional[str] = "15-20 min"
    rating: Optional[float] = 4.8
    allergens: Optional[List[str]] = []
    ingredients: Optional[List[str]] = []
    wine_pairing: Optional[str] = None
    is_available: Optional[bool] = True

class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    image: Optional[str] = None
    tags: Optional[List[str]] = None
    calories: Optional[int] = None
    prep_time: Optional[str] = None
    allergens: Optional[List[str]] = None
    ingredients: Optional[List[str]] = None
    wine_pairing: Optional[str] = None
    is_available: Optional[bool] = None

class MenuItemResponse(BaseModel):
    id: str
    name: str
    category: str
    description: str
    price: float
    image: str
    tags: List[str] = []
    calories: int
    prep_time: str
    rating: float
    reviews_count: int
    allergens: List[str] = []
    ingredients: List[str] = []
    wine_pairing: Optional[str] = None
    is_available: bool

    class Config:
        from_attributes = True

# Order Schemas
class OrderItemSchema(BaseModel):
    menu_item_id: Optional[str] = None
    item_name: str
    price: float
    quantity: int = 1
    special_instructions: Optional[str] = ""
    image: Optional[str] = None

class OrderCreate(BaseModel):
    customer_name: str
    customer_email: EmailStr
    customer_phone: Optional[str] = None
    delivery_address: Optional[str] = None
    order_type: str = "delivery"  # "delivery", "dine-in", "takeaway"
    items: List[OrderItemSchema]
    coupon_code: Optional[str] = None
    payment_method: str = "Credit Card"
    tip: Optional[float] = 0.0

class OrderStatusUpdate(BaseModel):
    status: str
    note: Optional[str] = None

class OrderResponse(BaseModel):
    id: str
    user_id: Optional[str] = None
    customer_name: str
    customer_email: str
    customer_phone: Optional[str] = None
    delivery_address: Optional[str] = None
    order_type: str
    subtotal: float
    tax: float
    delivery_fee: float
    discount: float
    tip: float
    total: float
    coupon_code: Optional[str] = None
    payment_method: str
    status: str
    tracking_timeline: List[Dict[str, Any]] = []
    items: List[OrderItemSchema] = []
    created_at: Any

    class Config:
        from_attributes = True

# Reservation Schemas
class ReservationCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str
    date: str
    time: str
    guests: int = 2
    area: str = "Dining Room"
    special_requests: Optional[str] = None

class ReservationResponse(BaseModel):
    id: str
    user_id: Optional[str] = None
    name: str
    email: str
    phone: str
    date: str
    time: str
    guests: int
    area: str
    special_requests: Optional[str] = None
    status: str
    created_at: Any

    class Config:
        from_attributes = True

# Review Schemas
class ReviewCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    dish_name: Optional[str] = None
    comment: str = Field(..., min_length=5, max_length=1000)

class ReviewResponse(BaseModel):
    id: str
    user_name: str
    user_avatar: Optional[str] = None
    rating: int
    dish_name: Optional[str] = None
    comment: str
    sentiment: str
    verified_order: bool
    integrity_score: float
    is_flagged: bool
    created_at: Any

    class Config:
        from_attributes = True

# Inquiry Schemas
class InquiryCreate(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    subject: str
    message: str

class InquiryResponse(BaseModel):
    id: str
    name: str
    email: str
    phone: Optional[str] = None
    subject: str
    message: str
    integrity_status: str
    status: str
    created_at: Any

    class Config:
        from_attributes = True

# AI Schemas
class AIChatRequest(BaseModel):
    message: str
    history: Optional[List[Dict[str, str]]] = []

class AIChatResponse(BaseModel):
    reply: str
    source: str
    suggested_dishes: Optional[List[str]] = []

class AIRecommendationRequest(BaseModel):
    mood: Optional[str] = None
    dietary: Optional[str] = None
    budget: Optional[str] = None

class AIMenuGenRequest(BaseModel):
    concept: str

class CouponValidateRequest(BaseModel):
    code: str
    subtotal: float
