import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import MenuItem, User
from app.schemas import MenuItemCreate, MenuItemUpdate, MenuItemResponse
from app.auth import require_admin

router = APIRouter(prefix="/menu", tags=["Menu Management"])

def format_menu_item(m: MenuItem) -> MenuItemResponse:
    tags = json.loads(m.tags) if m.tags else []
    allergens = json.loads(m.allergens) if m.allergens else []
    ingredients = json.loads(m.ingredients) if m.ingredients else []
    return MenuItemResponse(
        id=m.id,
        name=m.name,
        category=m.category,
        description=m.description,
        price=m.price,
        image=m.image,
        tags=tags,
        calories=m.calories or 500,
        prep_time=m.prep_time or "15-20 min",
        rating=m.rating or 4.8,
        reviews_count=m.reviews_count or 0,
        allergens=allergens,
        ingredients=ingredients,
        wine_pairing=m.wine_pairing,
        is_available=m.is_available
    )

@router.get("", response_model=List[MenuItemResponse])
def get_menu(
    category: Optional[str] = None,
    dietary: Optional[str] = None,
    search: Optional[str] = None,
    sort: Optional[str] = "recommended",
    db: Session = Depends(get_db)
):
    query = db.query(MenuItem)

    if category and category != "All":
        query = query.filter(MenuItem.category == category)

    if dietary and dietary != "All":
        query = query.filter(MenuItem.tags.contains(dietary))

    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(
            (MenuItem.name.ilike(search_term)) |
            (MenuItem.description.ilike(search_term)) |
            (MenuItem.ingredients.ilike(search_term))
        )

    items = query.all()

    # Sorting
    if sort == "price_asc":
        items.sort(key=lambda x: x.price)
    elif sort == "price_desc":
        items.sort(key=lambda x: x.price, reverse=True)
    elif sort == "rating":
        items.sort(key=lambda x: x.rating, reverse=True)
    else:  # recommended
        items.sort(key=lambda x: (1 if "Chef Special" in (x.tags or "") else 0, x.rating), reverse=True)

    return [format_menu_item(m) for m in items]

@router.get("/{item_id}", response_model=MenuItemResponse)
def get_menu_item(item_id: str, db: Session = Depends(get_db)):
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return format_menu_item(item)

@router.post("", response_model=MenuItemResponse, status_code=status.HTTP_201_CREATED)
def create_menu_item(
    data: MenuItemCreate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    new_item = MenuItem(
        name=data.name.strip(),
        category=data.category.strip(),
        description=data.description.strip(),
        price=data.price,
        image=data.image.strip(),
        tags=json.dumps(data.tags or []),
        calories=data.calories or 500,
        prep_time=data.prep_time or "15-20 min",
        rating=data.rating or 4.8,
        allergens=json.dumps(data.allergens or []),
        ingredients=json.dumps(data.ingredients or []),
        wine_pairing=data.wine_pairing,
        is_available=data.is_available if data.is_available is not None else True
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return format_menu_item(new_item)

@router.put("/{item_id}", response_model=MenuItemResponse)
def update_menu_item(
    item_id: str,
    data: MenuItemUpdate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    if data.name is not None:
        item.name = data.name.strip()
    if data.category is not None:
        item.category = data.category.strip()
    if data.description is not None:
        item.description = data.description.strip()
    if data.price is not None:
        item.price = data.price
    if data.image is not None:
        item.image = data.image.strip()
    if data.tags is not None:
        item.tags = json.dumps(data.tags)
    if data.calories is not None:
        item.calories = data.calories
    if data.prep_time is not None:
        item.prep_time = data.prep_time
    if data.allergens is not None:
        item.allergens = json.dumps(data.allergens)
    if data.ingredients is not None:
        item.ingredients = json.dumps(data.ingredients)
    if data.wine_pairing is not None:
        item.wine_pairing = data.wine_pairing
    if data.is_available is not None:
        item.is_available = data.is_available

    db.commit()
    db.refresh(item)
    return format_menu_item(item)

@router.patch("/{item_id}/toggle-availability", response_model=MenuItemResponse)
def toggle_item_availability(
    item_id: str,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    item.is_available = not item.is_available
    db.commit()
    db.refresh(item)
    return format_menu_item(item)

@router.delete("/{item_id}")
def delete_menu_item(
    item_id: str,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    db.delete(item)
    db.commit()
    return {"message": f"Dish '{item.name}' deleted successfully"}
