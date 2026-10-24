import datetime
import uuid
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    role = Column(String(20), default="customer")  # "customer" or "admin"
    phone = Column(String(50), nullable=True)
    address = Column(String(255), nullable=True)
    dietary_preferences = Column(Text, default="[]")  # JSON string array e.g. ["Nut Allergy", "Gluten-Free"]
    firebase_uid = Column(String(128), unique=True, index=True, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="user")
    reservations = relationship("Reservation", back_populates="user")

class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String(150), nullable=False, index=True)
    category = Column(String(50), nullable=False, index=True)
    description = Column(Text, nullable=False)
    price = Column(Float, nullable=False)
    image = Column(String(500), nullable=False)
    tags = Column(Text, default="[]")  # JSON string array
    calories = Column(Integer, default=500)
    prep_time = Column(String(50), default="15-20 min")
    rating = Column(Float, default=4.8)
    reviews_count = Column(Integer, default=0)
    allergens = Column(Text, default="[]")  # JSON string array
    ingredients = Column(Text, default="[]")  # JSON string array
    wine_pairing = Column(String(200), nullable=True)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Order(Base):
    __tablename__ = "orders"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    customer_name = Column(String(100), nullable=False)
    customer_email = Column(String(120), nullable=False)
    customer_phone = Column(String(50), nullable=True)
    delivery_address = Column(String(255), nullable=True)
    order_type = Column(String(30), default="delivery")  # "delivery", "dine-in", "takeaway"
    subtotal = Column(Float, nullable=False)
    tax = Column(Float, nullable=False)
    delivery_fee = Column(Float, default=0.0)
    discount = Column(Float, default=0.0)
    tip = Column(Float, default=0.0)
    total = Column(Float, nullable=False)
    coupon_code = Column(String(50), nullable=True)
    payment_method = Column(String(50), default="Credit Card")
    status = Column(String(50), default="pending")  # pending, preparing, quality_check, out_for_delivery, delivered, cancelled
    tracking_timeline = Column(Text, default="[]")  # JSON array of status history events
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(String, primary_key=True, default=generate_uuid)
    order_id = Column(String, ForeignKey("orders.id"), nullable=False)
    menu_item_id = Column(String, nullable=True)
    item_name = Column(String(150), nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, default=1)
    special_instructions = Column(String(255), default="")
    image = Column(String(500), nullable=True)

    order = relationship("Order", back_populates="items")

class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), nullable=False)
    phone = Column(String(50), nullable=False)
    date = Column(String(20), nullable=False)
    time = Column(String(20), nullable=False)
    guests = Column(Integer, default=2)
    area = Column(String(100), default="Dining Room")  # Chef's Counter, Patio, Dining Room, Private Alcove
    special_requests = Column(Text, nullable=True)
    status = Column(String(30), default="confirmed")  # confirmed, seated, completed, cancelled
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="reservations")

class Review(Base):
    __tablename__ = "reviews"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    user_name = Column(String(100), nullable=False)
    user_avatar = Column(String(500), nullable=True)
    rating = Column(Integer, nullable=False)
    dish_name = Column(String(150), nullable=True)
    comment = Column(Text, nullable=False)
    sentiment = Column(String(50), default="Positive")  # Extremely Positive, Positive, Neutral, Critical
    verified_order = Column(Boolean, default=True)
    integrity_score = Column(Float, default=0.98)
    is_flagged = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="reviews")

class Inquiry(Base):
    __tablename__ = "inquiries"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    email = Column(String(120), nullable=False)
    phone = Column(String(50), nullable=True)
    subject = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    integrity_status = Column(String(50), default="clean")
    status = Column(String(30), default="unread")  # unread, responded
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class IntegrityLog(Base):
    __tablename__ = "integrity_logs"

    id = Column(String, primary_key=True, default=generate_uuid)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    event_type = Column(String(80), nullable=False)  # order_allergy_check, price_tampering, review_moderation, spam_filter
    severity = Column(String(20), default="info")  # info, low, medium, high
    details = Column(Text, default="{}")  # JSON payload
    status = Column(String(30), default="passed")  # passed, warning, blocked

class Coupon(Base):
    __tablename__ = "coupons"

    id = Column(String, primary_key=True, default=generate_uuid)
    code = Column(String(50), unique=True, index=True, nullable=False)
    discount_percent = Column(Float, default=15.0)
    max_discount = Column(Float, default=30.0)
    min_order = Column(Float, default=40.0)
    description = Column(String(200), nullable=False)
    is_active = Column(Boolean, default=True)
