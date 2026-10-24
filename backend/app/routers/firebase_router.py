import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import MenuItem, User
from app.auth import get_optional_current_user, require_admin
from app.services.firebase_service import firebase_service
from app.config import settings

router = APIRouter(prefix="/firebase", tags=["Firebase Cloud"])

@router.get("/status")
def get_firebase_status():
    """Returns the current connection status and statistics for Firebase & Firestore."""
    return firebase_service.get_status()

@router.get("/config")
def get_firebase_client_config():
    """Returns the public Firebase web configuration for frontend client integration."""
    return {
        "projectId": settings.FIREBASE_PROJECT_ID,
        "authDomain": f"{settings.FIREBASE_PROJECT_ID}.firebaseapp.com",
        "databaseURL": f"https://{settings.FIREBASE_PROJECT_ID}.firebaseio.com",
        "storageBucket": f"{settings.FIREBASE_PROJECT_ID}.appspot.com",
        "isBackendConnected": firebase_service.is_connected()
    }

@router.post("/sync-menu")
def sync_menu_to_firestore(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Admin endpoint to batch-sync the entire Telugu menu catalog to Cloud Firestore."""
    items = db.query(MenuItem).all()
    menu_dicts = []
    for m in items:
        tags = []
        allergens = []
        ingredients = []
        try:
            tags = json.loads(m.tags) if m.tags else []
            allergens = json.loads(m.allergens) if m.allergens else []
            ingredients = json.loads(m.ingredients) if m.ingredients else []
        except Exception:
            pass

        menu_dicts.append({
            "id": m.id,
            "name": m.name,
            "category": m.category,
            "description": m.description,
            "price": m.price,
            "image": m.image,
            "tags": tags,
            "calories": m.calories,
            "prep_time": m.prep_time,
            "rating": m.rating,
            "allergens": allergens,
            "ingredients": ingredients,
            "is_available": m.is_available,
            "wine_pairing": m.wine_pairing
        })

    synced_count = firebase_service.sync_menu_items_to_firestore(menu_dicts)
    return {
        "success": True,
        "message": f"Successfully synchronized {synced_count} dishes to Cloud Firestore collection 'menu_items'",
        "count": synced_count,
        "mode": "Live Firestore" if firebase_service.is_connected() else "Simulated Sync Pipeline"
    }
