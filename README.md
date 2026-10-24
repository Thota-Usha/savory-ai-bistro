# 🍽️ Savory AI Bistro — Full-Stack Intelligent Restaurant Application

> **A royal, AI-powered Telugu & Andhra gastronomic restaurant web application featuring authentic regional delicacies (Andhra Kodi Vepudu, Hyderabadi Dum Biryani, Gongura Mamsam, Pootharekulu, etc.), Indian Rupee (₹) pricing, real-time culinary intelligence, persistent ordering, allergen integrity protection, dynamic menu management, and interactive table reservations.**

---

## 🌟 Key Capabilities & Architectural Features

### 1. 🤖 AI-Driven Integrity & Interaction
- **Ustaad Ananda Rao (Interactive AI Culinary Concierge & Sommelier)**: Real-time conversational AI gastronomy expert powered by Google Gemini 3.8 Flash (with built-in regional culinary heuristics). Recommends authentic Telugu pairings (e.g. Biryani with Masala Majjiga or Bellam Panakam), explains heritage cooking methods, and customizes spice levels.
- **AI Health & Allergen Collision Shield**: Automatically analyzes line items in the user's cart against their saved profile allergies (e.g. Nut Allergy, Dairy, Celiac/Gluten-Free) and flags instant safety alerts before ordering.
- **AI Price & Order Tampering Guard**: Validates catalog item IDs, authentic database INR pricing (₹), and promo discount thresholds to ensure strict transactional integrity.
- **AI Content Moderation & Sentiment Analysis**: Analyzes customer reviews for sentiment categorization (*Extremely Positive, Positive, Neutral, Critical*) while blocking spam and injection attempts.
- **Admin AI Menu Item Generator**: Automatically creates authentic Telugu sensory culinary titles, descriptions, allergen tags, and optimal ₹ pricing from natural language concepts.

### 2. 🔐 User Authentication & Account Management
- **Secure Registration & Login**: Encrypted passwords via `bcrypt` and stateless session management with signed JWT (`PyJWT`) bearer tokens.
- **Profile Customization**: Manage contact information, delivery street address, and dietary allergy tags.
- **Pre-Seeded Demo Accounts**:
  - **Demo Customer**: `jane@example.com` / `password123` (*Lakshmi Sree*)
  - **Executive Admin**: `admin@savorybistro.com` / `admin123` (*Ustaad Ananda Rao*)

### 3. 🍲 Dynamic Menu Management
- **22+ Authentic Telugu Dishes**: Categorized into *Prarambha / Starters, Chef's Royal Signatures, Kura & Sadham (Mains), Tiffins & Hearth, Mithai / Sweets, and Paanakam & Coolers*.
- **Accurate Telugu Names & Regional Heritage**: Guntur Mirchi Bajji, Andhra Kodi Vepudu, Royyala Vepudu, Mokkajonna Garelu, Hyderabadi Dum Biryani (Gosht), Natu Kodi Pulusu, Gongura Mamsam, Nellore Chepala Pulusu, Gutti Vankaya Koora, Ulava Charu with Cream & Ghee, Avakaya Mudda Pappu Annam, MLA Pesarattu, Rayalaseema Ragi Sangati, Atreyapuram Pootharekulu, Kobbari Bobbatlu, Qubani Ka Meetha, Double Ka Meetha, Bellam Panakam, and Masala Majjiga.
- **Indian Rupee (₹) Pricing**: Transparent regional pricing ranging from ₹110 to ₹520.
- **Search & Filter Navigation**: Instant real-time search across titles, ingredients, and descriptions.
- **Dietary Filter Chips**: One-click filtering by *Vegetarian, Vegan, Gluten-Free, Chef Special, and Spicy*.
- **Sorting Options**: Sort by *Chef Recommended, Top Rated, Price: Low to High, Price: High to Low*.
- **Admin Catalog CRUD**: Add new dishes, edit descriptions/pricing, toggle availability (*In Stock / Sold Out*), and delete items.

### 4. 🛒 Shopping Cart & Real-Time Ordering System
- **Persistent Cart**: Automatically saved across browser refreshes.
- **Line Item Customization**: Quantity stepper, removal, and item-level culinary cooking notes (e.g., *"Medium rare, dressing on side"*).
- **Promotional Coupon System**: Instant AI discount calculation (`WELCOME20`, `TASTE15`, `VIPBISTRO`).
- **Seamless Checkout**: Address auto-population, delivery/dine-in/takeaway toggles, tip calculator, and simulated payment methods.
- **Confetti Celebration & Live Order Tracking**: Animated 5-step progress tracker (*Order Placed -> Kitchen Prep -> Quality Check -> Out for Delivery -> Delivered*).

### 5. 📅 Table Reservations & Reviews
- **Table Booking Service**: Choose date, time slot, party size, and seating area (*Chef's Tasting Counter, Garden Patio, Main Dining Hall, Private Alcove*).
- **Verified Customer Reviews**: Star ratings, dish references, and AI integrity scores.
- **Contact Inquiries**: Validated inquiry submission with admin management.

### 6. 📊 Executive Admin Dashboard
- **Real-Time KPIs**: Total Revenue, Total Orders, Active Orders, Average Order Value, Customer Ratings, and AI Integrity Flagged Count.
- **Live Order Control**: Advance order statuses with single clicks.
- **AI Security & Audit Logs**: Detailed audit trail of all automated integrity validations.

---

## 💻 Tech Stack

| Layer | Technologies |
|---|---|
| **Backend** | Python 3.13, FastAPI 0.142, Uvicorn, SQLAlchemy 2.1, Pydantic v2, SQLite |
| **Security & Auth** | PyJWT (HS256), bcrypt password hashing, HTTPBearer |
| **AI Engine** | Google Gemini 3.8 Flash (`@google/genai` / HTTPX REST) + Built-in Culinary Heuristics Engine |
| **Frontend** | HTML5, CSS3, Modern ES6+ JavaScript, Tailwind CSS luxury design system, Canvas Confetti |
| **Typography** | Playfair Display & Plus Jakarta Sans via Google Fonts |

---

## 🚀 How to Open and Run in VS Code

### 1. Open Project in VS Code
Open VS Code and choose **File > Open Folder...**, then select:
```
C:\Users\USHA SREE\.gemini\antigravity\scratch\savory-ai-bistro
```

### 2. Method A: One-Click Startup (Recommended)
Simply double-click the **`run.bat`** file in the root directory!
- Automatically activates the virtual environment
- Starts the FastAPI server on `http://127.0.0.1:8000`
- Launches the application in your default browser

### 3. Method B: Using VS Code Run & Debug (F5)
1. Press `F5` or click **Run and Debug** in the VS Code sidebar.
2. Select **"Savory AI Bistro: Run Full-Stack Server"**.
3. Open your browser and navigate to:
   - **Web Application**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
   - **Interactive Swagger API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
   - **Redoc Documentation**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### 4. Method C: Manual Terminal Command
```bash
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

---

## 🔑 Default Login Credentials

| Role | Email | Password | Access Level |
|---|---|---|---|
| **Customer** | `jane@example.com` | `password123` | Ordering, Cart, Reservations, Profile, Reviews |
| **Admin** | `admin@savorybistro.com` | `admin123` | Full Dashboard, Order Management, Menu CRUD, AI Dish Creator, Audit Logs |

*(You can also use the 1-click demo login buttons directly inside the Sign In modal!)*

---

## 📁 Project Directory Structure

```
savory-ai-bistro/
├── .vscode/
│   ├── launch.json           # VS Code F5 debugger configuration
│   └── settings.json         # Python interpreter and workspace preferences
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py           # FastAPI application entry point
│   │   ├── config.py         # App configuration & JWT settings
│   │   ├── database.py       # SQLAlchemy engine & SQLite session
│   │   ├── models.py         # Database models (User, Menu, Order, etc.)
│   │   ├── schemas.py        # Pydantic request & response schemas
│   │   ├── auth.py           # JWT token creation & bcrypt hashing
│   │   ├── seed.py           # Seed data for Michelin menu items & demo accounts
│   │   ├── services/
│   │   │   ├── ai_service.py        # Gemini 3.8 Flash & culinary chatbot engine
│   │   │   ├── integrity_service.py # AI price check, allergy collision, moderation
│   │   │   └── firebase_service.py  # Firebase Admin SDK & Cloud Firestore real-time sync
│   │   └── routers/
│   │       ├── auth_router.py       # JWT & Firebase ID Token OAuth login
│   │       ├── menu_router.py
│   │       ├── order_router.py      # Order placement & Firestore sync
│   │       ├── reservation_router.py# Table bookings & Firestore sync
│   │       ├── review_router.py
│   │       ├── contact_router.py
│   │       ├── ai_router.py
│   │       ├── admin_router.py
│   │       └── firebase_router.py   # Firebase Cloud status & Firestore batch sync
│   ├── venv/                        # Pre-configured Python virtual environment
│   ├── firebase-credentials.example.json # Service account template
│   └── restaurant.db                # SQLite database file
├── frontend/
│   ├── index.html                   # Luxury Single Page Application
│   ├── styles.css                   # Custom luxury culinary stylesheet
│   └── app.js                       # State management, cart, Firebase Auth & admin
├── run.bat                          # 1-click Windows runner
├── requirements.txt                 # Python dependency list
├── .env.example                     # Environment variables template
└── README.md                        # Complete documentation
```

---

## 🔥 Firebase Cloud Integration

The application connects to **Google Firebase** via the official `firebase-admin` SDK:
- **Cloud Firestore Real-Time Sync**: Orders, table reservations, reviews, and dishes sync directly to Firestore collections (`orders`, `reservations`, `reviews`, `menu_items`).
- **Firebase Authentication**: Patrons can sign in with Firebase / Google OAuth tokens (`POST /api/auth/firebase-login`).
- **1-Click Menu Sync**: Batch sync the complete 22-dish authentic Telugu menu directly to Firestore with one click from the Admin Dashboard or via `POST /api/firebase/sync-menu`.
- **Linking Your Own Live Firebase Project**:
  1. Open [Firebase Console](https://console.firebase.google.com/) -> **Project Settings** -> **Service Accounts**.
  2. Click **Generate New Private Key** and download the JSON file.
  3. Place it as `backend/firebase-credentials.json` (or set `FIREBASE_CREDENTIALS_PATH` in `backend/.env`).
  4. Live Cloud Firestore syncing and token validation activate instantly with zero server restarts needed!

---

## 🛡️ AI Data Integrity Highlights

1. **Transactional Price Verification**: The backend recalculates each line-item against the verified database price, preventing any client-side payload tampering.
2. **Allergen Collision Shield**: When users with saved dietary preferences (e.g., *Nut Allergy*) place items containing allergens into their cart, an alert banner immediately highlights the health conflict.
3. **Sentiment & Safety Moderation**: Guest reviews are evaluated for XSS, script injection, and sentiment classification before publishing.
4. **Audit Logging**: Every validation event is logged with severity and inspection details, accessible in the Admin Portal.
