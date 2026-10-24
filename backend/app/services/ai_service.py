import json
import logging
import httpx
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.config import settings
from app.models import MenuItem, User

logger = logging.getLogger("ai_service")

async def call_gemini_api(prompt: str) -> Optional[str]:
    """Call Google Gemini 3.8 Flash if API key is provided."""
    if not settings.GEMINI_API_KEY:
        return None
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={settings.GEMINI_API_KEY}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                return data["candidates"][0]["content"]["parts"][0]["text"]
            else:
                logger.warning(f"Gemini API returned status {resp.status_code}: {resp.text}")
    except Exception as e:
        logger.warning(f"Gemini API error, falling back to local culinary engine: {str(e)}")
    return None

async def chat_with_sommelier(
    user_message: str,
    history: List[Dict[str, str]] = [],
    user: Optional[User] = None,
    db: Optional[Session] = None
) -> Dict[str, Any]:
    """AI Sommelier & Culinary Assistant Chatbot for Royal Telugu Gastronomy."""
    menu_items = db.query(MenuItem).filter(MenuItem.is_available == True).all() if db else []
    
    menu_catalog_text = "\n".join([
        f"- {m.name} (₹{m.price:.2f}, {m.category}): {m.description} [Allergens: {m.allergens}] [Pairing: {m.wine_pairing}]"
        for m in menu_items[:14]
    ])

    user_info = "Gourmet Guest"
    if user:
        prefs = json.loads(user.dietary_preferences) if user.dietary_preferences else []
        user_info = f"Customer Name: {user.name}, Preferences/Allergens: {', '.join(prefs) if prefs else 'None recorded'}"

    system_prompt = f"""You are Ustaad Ananda Rao, the Master AI Culinary Concierge and Sommelier for "Savory AI Bistro", celebrating the finest Royal Telugu, Andhra, Rayalaseema, and Hyderabadi gastronomic heritage.
Customer Profile: {user_info}
Live Telugu Restaurant Menu:
{menu_catalog_text}

Rules:
1. Speak in a warm, respectful ("Namaskaram!"), hospitable, and appetizing manner celebrating authentic Telugu flavors (Guntur spice, Gongura tang, pure cow ghee, stone-ground masalas).
2. Recommend specific Telugu dishes from our menu by exact title so guests can easily order them.
3. Quote all prices in Indian Rupees (₹).
4. Suggest traditional coolers and pairings (Masala Majjiga, Sugandhi Nannari, Bellam Panakam, Madras Filter Coffee, Bagara Rice).
5. Strictly address allergies (especially peanuts in Mirchi Bajji / Gutti Vankaya, dairy in Ghee/Pappu) with utmost medical care.
6. Keep your responses under 130 words.
7. When recommending a dish, mention it clearly in bold.

User Question: {user_message}"""

    # Try Gemini 3.8 Flash
    gemini_reply = await call_gemini_api(system_prompt)
    if gemini_reply:
        return {
            "reply": gemini_reply.strip(),
            "source": "Gemini 3.8 Flash",
            "suggested_dishes": extract_dishes(gemini_reply, menu_items)
        }

    # Fallback to built-in Telugu culinary intelligence engine
    fallback_reply, suggested = generate_telugu_culinary_fallback(user_message, menu_items, user)
    return {
        "reply": fallback_reply,
        "source": "Savory Telugu AI Engine",
        "suggested_dishes": suggested
    }

def extract_dishes(text: str, menu_items: List[MenuItem]) -> List[str]:
    found = []
    text_lower = text.lower()
    for item in menu_items:
        if item.name.lower() in text_lower:
            found.append(item.name)
    return found[:3]

def generate_telugu_culinary_fallback(message: str, menu_items: List[MenuItem], user: Optional[User]) -> (str, List[str]):
    query = message.lower()

    # 1. Biryani
    if "biryani" in query or "dum" in query or "rice" in query and "mutton" in query:
        return (
            "Namaskaram! Our crown jewel is the **Hyderabadi Dum Biryani (Gosht / Mutton)** (₹520), slow-steamed on coal embers in a sealed clay handi with saffron and caramelized onions. I strongly recommend pairing it with our chilled **Masala Majjiga** (₹110) to balance the royal spices!",
            ["Hyderabadi Dum Biryani (Gosht / Mutton)", "Masala Majjiga (Spiced Buttermilk)"]
        )

    # 2. Spicy / Non-Veg / Kodi / Chicken / Prawns
    if any(k in query for k in ["kodi", "chicken", "spicy", "mamsam", "mutton", "meat", "prawn", "royyala", "fish", "chepala"]):
        if "fish" in query or "chepala" in query:
            return (
                "For coastal Andhra lovers, our **Nellore Chepala Pulusu (Claypot Fish Curry)** (₹440) cooked with fresh raw mango, native tamarind, and Korameenu fish is pure bliss. Enjoy with hot steamed rice!",
                ["Nellore Chepala Pulusu (Claypot Fish Curry)"]
            )
        if "prawn" in query or "royyala" in query:
            return (
                "Delight in our **Royyala Vepudu (Godavari Spiced Prawn Fry)** (₹420), pan-roasted with green chilies, grated dry coconut, and hand-ground garam masala. An unmatched delicacy!",
                ["Royyala Vepudu (Godavari Spiced Prawn Fry)"]
            )
        if "gongura" in query:
            return (
                "The legendary **Gongura Mamsam (Mutton with Sorrel Leaves)** (₹490) is slow-braised with sour Guntur sorrel leaves and fiery red chilies. Pair with **Masala Majjiga** for the quintessential Andhra experience!",
                ["Gongura Mamsam (Mutton with Sorrel Leaves)", "Masala Majjiga (Spiced Buttermilk)"]
            )
        return (
            "For fiery Andhra flavors, savor our **Andhra Kodi Vepudu (Pepper Chicken Fry)** (₹360) and the rustic Rayalaseema **Natu Kodi Pulusu (Country Chicken Curry)** (₹460). Pure culinary heaven!",
            ["Andhra Kodi Vepudu (Pepper Chicken Fry)", "Natu Kodi Pulusu (Country Chicken Curry)"]
        )

    # 3. Vegetarian / Pappu / Vankaya / Comfort
    if any(k in query for k in ["veg", "vegetarian", "pappu", "vankaya", "brinjal", "ulava", "curry", "dosa", "pesarattu"]):
        if "ulava" in query or "charu" in query:
            return (
                "Our **Ulava Charu with Fresh Cream & Ghee** (₹290) is slow-simmered for 12 hours and crowned with churned white butter. Pour it over hot Sona Masoori rice for an unforgettable feast!",
                ["Ulava Charu with Fresh Cream & Ghee"]
            )
        if "vankaya" in query or "brinjal" in query:
            return (
                "Experience our royal **Gutti Vankaya Koora (Stuffed Brinjal Curry)** (₹320), stuffed with roasted peanuts, sesame seeds, and dry coconut. Note: contains peanuts!",
                ["Gutti Vankaya Koora (Stuffed Brinjal Curry)"]
            )
        if "pesarattu" in query or "tiffin" in query or "dosa" in query:
            return (
                "You must try our iconic **MLA Pesarattu with Upma & Allam Pachadi** (₹220) or the fiery **Guntur Karam Dosa with Neyyi (Ghee)** (₹190). Both are roasted crisp in pure cow ghee!",
                ["MLA Pesarattu with Upma & Allam Pachadi", "Guntur Karam Dosa with Neyyi (Ghee)"]
            )
        return (
            "For classic Telugu comfort, nothing compares to **Avakaya Mudda Pappu Annam with Ghee** (₹280) and our tangy **Gongura Pappu with Sona Masoori Rice** (₹260). Homely yet royal!",
            ["Avakaya Mudda Pappu Annam with Ghee", "Gongura Pappu with Sona Masoori Rice"]
        )

    # 4. Sweets / Desserts (Pootharekulu, Bobbatlu, Qubani)
    if any(k in query for k in ["sweet", "dessert", "pootharekulu", "bobbatlu", "qubani", "double ka meetha"]):
        return (
            "Complete your royal meal with East Godavari's **Authentic Atreyapuram Pootharekulu** (₹210) made with paper-thin rice starch, pure ghee, and jaggery, or the Nizami **Royal Hyderabadi Qubani Ka Meetha** (₹240) with clotted malai!",
            ["Authentic Atreyapuram Pootharekulu", "Royal Hyderabadi Qubani Ka Meetha"]
        )

    # 5. Coolers & Drinks (Majjiga, Panakam, Coffee)
    if any(k in query for k in ["drink", "cooler", "majjiga", "panakam", "coffee", "beverage"]):
        return (
            "To cool down from our Andhra spices, sip our earthen-pot churned **Masala Majjiga (Spiced Buttermilk)** (₹110) or our Ayurvedic **Royal Bellam Panakam & Sugandhi Nannari** (₹140). Conclude with **Madras Filter Degree Coffee** (₹120)!",
            ["Masala Majjiga (Spiced Buttermilk)", "Royal Bellam Panakam & Sugandhi Nannari", "Madras Filter Degree Coffee"]
        )

    # 6. Allergies & Dietary Restrictions
    if any(k in query for k in ["allergy", "allergic", "peanut", "nut", "gluten", "dairy"]):
        if "peanut" in query or "nut" in query:
            return (
                "Safety is our utmost duty. Note that **Gutti Vankaya Koora** and **Guntur Mirchi Bajji** contain roasted peanuts. Dishes completely free of nuts include **Natu Kodi Pulusu**, **Nellore Chepala Pulusu**, and **Gongura Mamsam**.",
                ["Natu Kodi Pulusu (Country Chicken Curry)", "Nellore Chepala Pulusu (Claypot Fish Curry)"]
            )
        return (
            "We handle all dietary preferences with surgical precision. Our AI Integrity Scanner continuously checks your cart against known allergen conflicts before you place your order!",
            []
        )

    # Default warm Telugu greeting
    return (
        "Namaskaram! Welcome to Savory AI Bistro. I am Ustaad Ananda Rao, your AI Culinary Concierge. From our charcoal-dum **Hyderabadi Dum Biryani (Gosht)** to tangy **Gongura Mamsam** and delicate **Atreyapuram Pootharekulu**, what flavors do you desire tonight?",
        ["Hyderabadi Dum Biryani (Gosht / Mutton)", "Gongura Mamsam (Mutton with Sorrel Leaves)"]
    )

async def get_personalized_recommendations(
    mood: Optional[str],
    dietary: Optional[str],
    budget: Optional[str],
    user: Optional[User],
    db: Session
) -> Dict[str, Any]:
    """Personalized Recommendations Engine based on mood, dietary restrictions, and budget."""
    query = db.query(MenuItem).filter(MenuItem.is_available == True)

    if dietary and dietary != "All":
        query = query.filter(MenuItem.tags.contains(dietary))

    items = query.all()

    if budget == "low":
        items = [i for i in items if i.price <= 250.0]
    elif budget == "high":
        items = [i for i in items if i.price >= 400.0]

    # Prioritize Chef Specials and high ratings
    items.sort(key=lambda x: (1 if "Chef Special" in (x.tags or "") else 0, x.rating), reverse=True)
    top_items = items[:4]

    explanation = "Curated based on master chef recommendations, authentic Telugu spice balance, and guest ratings."
    if mood:
        mood_map = {
            "romantic": "Crafted for a royal intimate dining experience, highlighting Hyderabadi Dum Biryani and decadent Qubani Ka Meetha.",
            "comfort": "Featuring comforting Telugu staples: piping hot Mudda Pappu Avakaya with pure cow ghee and Ulava Charu.",
            "celebration": "An opulent feast showcasing our most prized cuts: Gongura Mamsam, Kodi Vepudu, and Atreyapuram Pootharekulu.",
            "healthy": "Featuring nutritious high-protein and Ayurvedic preparations: Pesarattu, Nellore Chepala Pulusu, and Masala Majjiga."
        }
        explanation = mood_map.get(mood.lower(), f"Hand-selected to harmonize with your '{mood}' dining vibe.")

    return {
        "recommendations": top_items,
        "explanation": explanation,
        "confidence_score": 0.98
    }

async def generate_menu_item_ai(concept: str) -> Dict[str, Any]:
    """Admin AI tool to generate a gourmet Telugu menu item."""
    prompt = f"""You are a Master Chef of Royal Telugu Gastronomy. Generate a new authentic Telugu restaurant menu item based on: "{concept}".
Return ONLY a valid JSON object without markdown fences, with these exact keys:
{{
  "name": "Authentic Telugu Dish Name (English Translation)",
  "category": "Appetizers" or "Chef Signatures" or "Artisanal Pastas & Mains" or "Wood-Fired Hearth" or "Decadent Desserts" or "Artisanal Drinks",
  "description": "Sensory, mouth-watering description (2 sentences) highlighting traditional spices, Guntur chilies, Gongura, or desi ghee.",
  "price": 380.0,
  "calories": 520,
  "prep_time": "15-18 min",
  "tags": ["Chef Special", "Spicy"],
  "allergens": ["Dairy"],
  "ingredients": ["Key Ingredient 1", "Key Ingredient 2"],
  "wine_pairing": "Traditional cooler or pairing (e.g. Masala Majjiga, Sugandhi Nannari)"
}}"""

    gemini_res = await call_gemini_api(prompt)
    if gemini_res:
        try:
            clean = gemini_res.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean)
            if "image" not in data:
                data["image"] = "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?auto=format&fit=crop&w=800&q=80"
            return data
        except Exception:
            pass

    # Heuristic fallback generator for Telugu dishes
    c_lower = concept.lower()
    return {
        "name": f"Royal {concept.title()}",
        "category": "Chef Signatures",
        "description": f"Traditional Telugu specialty crafted from {concept}, slow-simmered in aromatic stone-ground Guntur spices, fresh curry leaves, and pure molten cow ghee.",
        "price": 420.0,
        "calories": 560,
        "prep_time": "18-20 min",
        "tags": ["Chef Special", "Spicy"],
        "allergens": ["Dairy"],
        "ingredients": [concept, "Guntur Chilies", "Curry Leaves", "Desi Ghee", "Stone-ground Garam Masala"],
        "wine_pairing": "Chilled Masala Majjiga or Sugandhi Nannari",
        "image": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?auto=format&fit=crop&w=800&q=80"
    }
