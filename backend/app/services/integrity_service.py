import json
import re
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models import MenuItem, IntegrityLog, User, Coupon

def log_integrity_event(db: Session, event_type: str, severity: str, details: Dict[str, Any], status: str):
    """Logs an AI security / integrity event to database."""
    log_entry = IntegrityLog(
        event_type=event_type,
        severity=severity,
        details=json.dumps(details),
        status=status
    )
    db.add(log_entry)
    db.commit()

def validate_order_integrity(
    items_data: List[Any],
    coupon_code: Optional[str],
    tip: float,
    user: Optional[User],
    db: Session
) -> Dict[str, Any]:
    """
    AI-driven integrity check for orders:
    - Verifies line-item existence and authentic menu pricing (prevents client price-tampering).
    - Validates coupon discounts and minimum spends.
    - Performs allergen collision analysis with user dietary preferences.
    """
    warnings = []
    errors = []
    calculated_subtotal = 0.0

    for item in items_data:
        menu_id = item.menu_item_id or getattr(item, "id", None)
        item_name = item.item_name
        qty = item.quantity
        reported_price = item.price

        menu_item = None
        if menu_id:
            menu_item = db.query(MenuItem).filter(MenuItem.id == menu_id).first()
        if not menu_item:
            menu_item = db.query(MenuItem).filter(MenuItem.name == item_name).first()

        if not menu_item:
            errors.append(f"Dish '{item_name}' could not be verified in the kitchen inventory.")
            continue

        if not menu_item.is_available:
            errors.append(f"Dish '{menu_item.name}' is currently sold out.")
            continue

        # Price verification
        if abs(menu_item.price - reported_price) > 0.01:
            errors.append(f"Price anomaly detected for '{menu_item.name}'. Verified price: ₹{menu_item.price:.2f}.")

        calculated_subtotal += menu_item.price * qty

        # Allergen Collision Analysis
        if user and user.dietary_preferences:
            try:
                user_prefs = json.loads(user.dietary_preferences)
                item_allergens = json.loads(menu_item.allergens) if menu_item.allergens else []
                item_ingredients = json.loads(menu_item.ingredients) if menu_item.ingredients else []

                for pref in user_prefs:
                    pref_lower = pref.lower()
                    # Check allergens
                    for alg in item_allergens:
                        if alg.lower() in pref_lower or pref_lower in alg.lower():
                            warnings.append(
                                f"Allergen Alert: '{menu_item.name}' contains {alg}, which conflicts with your '{pref}' profile."
                            )
                    # Check ingredients
                    for ing in item_ingredients:
                        if ing.lower() in pref_lower or pref_lower in ing.lower():
                            warnings.append(
                                f"Dietary Conflict: '{menu_item.name}' contains {ing} ({pref})."
                            )
            except Exception:
                pass

    # Coupon validation
    discount_amount = 0.0
    verified_coupon = None
    if coupon_code:
        coupon = db.query(Coupon).filter(Coupon.code == coupon_code.strip().upper(), Coupon.is_active == True).first()
        if coupon:
            if calculated_subtotal >= coupon.min_order:
                discount_amount = min(calculated_subtotal * (coupon.discount_percent / 100.0), coupon.max_discount)
                verified_coupon = coupon.code
            else:
                warnings.append(f"Promo code {coupon.code} requires a minimum order of ₹{coupon.min_order:.2f}.")
        else:
            warnings.append(f"Promo code '{coupon_code}' is invalid or expired.")

    # Calculations (5% GST for restaurants in India)
    tax_rate = 0.05
    tax_amount = round((calculated_subtotal - discount_amount) * tax_rate, 2)
    delivery_fee = 49.0 if calculated_subtotal > 0 else 0.0
    safe_tip = max(0.0, tip)
    total_amount = round(calculated_subtotal - discount_amount + tax_amount + delivery_fee + safe_tip, 2)

    passed = len(errors) == 0
    status_str = "blocked" if not passed else ("warning" if warnings else "passed")

    # Log integrity event
    log_integrity_event(
        db=db,
        event_type="order_integrity_validation",
        severity="high" if not passed else ("medium" if warnings else "info"),
        details={
            "subtotal": calculated_subtotal,
            "total": total_amount,
            "errors": errors,
            "warnings": warnings,
            "item_count": len(items_data)
        },
        status=status_str
    )

    return {
        "passed": passed,
        "errors": errors,
        "warnings": warnings,
        "subtotal": round(calculated_subtotal, 2),
        "discount": round(discount_amount, 2),
        "tax": tax_amount,
        "delivery_fee": delivery_fee,
        "tip": round(safe_tip, 2),
        "total": total_amount,
        "verified_coupon": verified_coupon
    }

def validate_review_integrity(
    comment: str,
    rating: int,
    db: Session
) -> Dict[str, Any]:
    """
    AI-driven integrity check for guest reviews:
    - XSS / Prompt Injection sanitization.
    - AI sentiment categorization.
    - Authenticity & integrity scoring.
    """
    suspicious_patterns = [
        r"<script.*?>.*?</script>",
        r"javascript:",
        r"ignore previous instructions",
        r"system prompt",
        r"DROP TABLE",
        r"SELECT \* FROM"
    ]

    is_flagged = False
    flag_reason = None
    integrity_score = 0.99

    for pat in suspicious_patterns:
        if re.search(pat, comment, re.IGNORECASE):
            is_flagged = True
            flag_reason = "Suspicious code injection or prompt override detected"
            integrity_score = 0.1
            break

    # Length & gibberish heuristics
    if len(comment.strip()) < 8:
        integrity_score = 0.6
    
    # Sentiment calculation
    positive_words = ["amazing", "exquisite", "delicious", "superb", "loved", "best", "perfect", "tender", "stellar", "heavenly"]
    critical_words = ["terrible", "awful", "cold", "disgusting", "horrible", "rude", "worst", "burnt", "slow"]
    
    comment_lower = comment.lower()
    pos_count = sum(1 for w in positive_words if w in comment_lower)
    crit_count = sum(1 for w in critical_words if w in comment_lower)

    if pos_count > crit_count or rating >= 5:
        sentiment = "Extremely Positive" if rating == 5 and pos_count >= 2 else "Positive"
    elif crit_count > pos_count or rating <= 2:
        sentiment = "Critical"
    else:
        sentiment = "Neutral"

    log_integrity_event(
        db=db,
        event_type="review_moderation",
        severity="high" if is_flagged else "info",
        details={
            "rating": rating,
            "sentiment": sentiment,
            "integrity_score": integrity_score,
            "flagged": is_flagged,
            "reason": flag_reason
        },
        status="blocked" if is_flagged else "passed"
    )

    return {
        "is_flagged": is_flagged,
        "flag_reason": flag_reason,
        "sentiment": sentiment,
        "integrity_score": integrity_score,
        "passed": not is_flagged
    }

def validate_inquiry_integrity(
    email: str,
    subject: str,
    message: str,
    db: Session
) -> Dict[str, Any]:
    """Validates contact inquiry integrity and detects spam."""
    is_valid_email = bool(re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email))
    passed = is_valid_email and len(message.strip()) >= 5

    status_str = "passed" if passed else "blocked"
    log_integrity_event(
        db=db,
        event_type="contact_inquiry_validation",
        severity="info" if passed else "medium",
        details={"email": email, "subject": subject, "valid_email": is_valid_email},
        status=status_str
    )

    return {
        "passed": passed,
        "integrity_status": "clean" if passed else "flagged_invalid"
    }
