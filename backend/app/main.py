import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.database import engine, Base, SessionLocal
from app.seed import seed_database
from app.routers import (
    auth_router,
    menu_router,
    order_router,
    reservation_router,
    review_router,
    contact_router,
    ai_router,
    admin_router,
    firebase_router
)

# Initialize database schema
Base.metadata.create_all(bind=engine)

# Seed database with initial menu items and users
with SessionLocal() as db_session:
    seed_database(db_session)

# Initialize FastAPI App
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Full-Stack AI-Powered Restaurant Web Application with Culinary Intelligence, Real-Time Ordering, and Dynamic Management"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(auth_router.router, prefix=settings.API_PREFIX)
app.include_router(menu_router.router, prefix=settings.API_PREFIX)
app.include_router(order_router.router, prefix=settings.API_PREFIX)
app.include_router(reservation_router.router, prefix=settings.API_PREFIX)
app.include_router(review_router.router, prefix=settings.API_PREFIX)
app.include_router(contact_router.router, prefix=settings.API_PREFIX)
app.include_router(ai_router.router, prefix=settings.API_PREFIX)
app.include_router(admin_router.router, prefix=settings.API_PREFIX)
app.include_router(firebase_router.router, prefix=settings.API_PREFIX)

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "ai_engine": "Gemini 3.8 Flash + Culinary AI Heuristics"
    }

# Mount Frontend static files
FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
