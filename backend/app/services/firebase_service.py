import os
import json
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from app.config import settings

logger = logging.getLogger("savory.firebase")
logger.setLevel(logging.INFO)

# Firebase Admin components
try:
    import firebase_admin
    from firebase_admin import credentials, auth, firestore
    FIREBASE_ADMIN_INSTALLED = True
except ImportError:
    FIREBASE_ADMIN_INSTALLED = False
    firebase_admin = None
    credentials = None
    auth = None
    firestore = None


class FirebaseService:
    def __init__(self):
        self.app: Optional[Any] = None
        self.db: Optional[Any] = None
        self.is_live: bool = False
        self.project_id: str = settings.FIREBASE_PROJECT_ID or "savory-ai-bistro"
        self.stats = {
            "orders_synced": 0,
            "reservations_synced": 0,
            "reviews_synced": 0,
            "menu_items_synced": 0,
            "last_sync_timestamp": None,
            "last_error": None
        }
        self._initialize_firebase()

    def _find_credentials_file(self) -> Optional[Path]:
        """Look for service account json in common local paths or settings."""
        if settings.FIREBASE_CREDENTIALS_PATH:
            p = Path(settings.FIREBASE_CREDENTIALS_PATH)
            if p.is_file():
                return p

        # Check standard default paths
        base_backend = Path(__file__).resolve().parent.parent.parent
        candidates = [
            base_backend / "firebase-credentials.json",
            base_backend / "firebase-service-account.json",
            base_backend.parent / "firebase-credentials.json",
            base_backend / "app" / "firebase-credentials.json",
        ]
        for c in candidates:
            if c.is_file():
                return c
        return None

    def _initialize_firebase(self):
        """Safely initializes Firebase Admin SDK with fallback to simulation mode."""
        if not FIREBASE_ADMIN_INSTALLED:
            logger.warning("[FIREBASE] firebase-admin package is not installed.")
            self.is_live = False
            return

        cred_file = self._find_credentials_file()
        cred_json_env = settings.FIREBASE_CREDENTIALS_JSON

        try:
            # Avoid re-initializing if already default app exists
            if firebase_admin._apps:
                self.app = firebase_admin.get_app()
                self.db = firestore.client(self.app)
                self.is_live = True
                logger.info("[FIREBASE] Connected to existing Firebase Admin app.")
                return

            if cred_file:
                logger.info(f"[FIREBASE] Initializing with service account file: {cred_file}")
                cred = credentials.Certificate(str(cred_file))
                self.app = firebase_admin.initialize_app(cred, {
                    "projectId": self.project_id
                })
                self.db = firestore.client(self.app)
                self.is_live = True
                logger.info(f"[FIREBASE] Successfully connected to Firebase Project: {self.project_id}")
            elif cred_json_env:
                logger.info("[FIREBASE] Initializing with FIREBASE_CREDENTIALS_JSON environment variable.")
                cred_dict = json.loads(cred_json_env)
                cred = credentials.Certificate(cred_dict)
                self.app = firebase_admin.initialize_app(cred, {
                    "projectId": self.project_id
                })
                self.db = firestore.client(self.app)
                self.is_live = True
                logger.info(f"[FIREBASE] Successfully connected to Firebase Project via JSON env.")
            else:
                logger.info(
                    "[FIREBASE] No service account file found (e.g. backend/firebase-credentials.json). "
                    "Running in Hybrid / Simulated Firebase Mode. All API operations will function seamlessly."
                )
                self.is_live = False
        except Exception as exc:
            self.stats["last_error"] = str(exc)
            logger.error(f"[FIREBASE] Initialization error: {exc}. Operating in simulation fallback mode.")
            self.is_live = False

    def is_connected(self) -> bool:
        return self.is_live and self.db is not None

    def get_status(self) -> Dict[str, Any]:
        """Provides status and connectivity details for admin dashboard."""
        return {
            "connected": self.is_live,
            "mode": "Live Firebase Cloud (Firestore & Auth)" if self.is_live else "Simulation / Ready for Credentials",
            "project_id": self.project_id,
            "admin_sdk_installed": FIREBASE_ADMIN_INSTALLED,
            "services": {
                "authentication": self.is_live,
                "firestore_database": self.is_live,
                "cloud_realtime_sync": settings.FIREBASE_SYNC_ENABLED
            },
            "sync_statistics": self.stats,
            "credentials_file_detected": bool(self._find_credentials_file()),
            "setup_guide": {
                "step_1": "Go to Firebase Console -> Project Settings -> Service accounts.",
                "step_2": "Click 'Generate new private key' and download the JSON file.",
                "step_3": "Save it as 'backend/firebase-credentials.json' in this project or set FIREBASE_CREDENTIALS_PATH in backend/.env.",
                "step_4": "Restart server or test connection - live Firestore syncing & Auth activates instantly."
            }
        }

    # =========================================================================
    # FIREBASE AUTHENTICATION
    # =========================================================================
    def verify_firebase_token(self, id_token: str) -> Dict[str, Any]:
        """
        Verifies a Firebase ID token from client.
        In live mode: Uses official Firebase Admin SDK auth.verify_id_token.
        In dev/sim mode: Allows testing mock tokens seamlessly.
        """
        if not id_token:
            raise ValueError("Firebase ID token cannot be empty")

        if self.is_live and auth:
            try:
                decoded = auth.verify_id_token(id_token)
                return {
                    "uid": decoded.get("uid"),
                    "email": decoded.get("email"),
                    "name": decoded.get("name", "Firebase User"),
                    "phone": decoded.get("phone_number"),
                    "picture": decoded.get("picture"),
                    "provider": decoded.get("firebase", {}).get("sign_in_provider", "google.com")
                }
            except Exception as e:
                logger.error(f"[FIREBASE AUTH] Token verification failed: {e}")
                raise ValueError(f"Invalid Firebase ID token: {str(e)}")

        # Simulation Mode: Parse mock token for development & testing
        if id_token.startswith("mock-") or "test" in id_token:
            return {
                "uid": f"firebase_sim_{id_token[:12]}",
                "email": f"customer_{id_token[:6]}@savorybistro.com",
                "name": "Savory Royal Patron",
                "phone": "+91 98490 12345",
                "picture": None,
                "provider": "google.com"
            }

        # If a non-mock token passed but not configured yet:
        raise ValueError(
            "Live Firebase credentials are not yet linked to verify production Firebase tokens. "
            "Please provide backend/firebase-credentials.json or use simulated test credentials."
        )

    # =========================================================================
    # FIRESTORE CLOUD DATABASE SYNC
    # =========================================================================
    def sync_order_to_firestore(self, order_dict: Dict[str, Any]) -> bool:
        """Syncs an order to Cloud Firestore collection 'orders'."""
        if not settings.FIREBASE_SYNC_ENABLED:
            return False

        order_id = str(order_dict.get("id"))
        self.stats["orders_synced"] += 1
        import datetime
        self.stats["last_sync_timestamp"] = datetime.datetime.utcnow().isoformat()

        if self.is_live and self.db:
            try:
                doc_ref = self.db.collection("orders").document(order_id)
                doc_ref.set(order_dict, merge=True)
                logger.info(f"[FIRESTORE] Synced Order #{order_id} to Cloud Firestore")
                return True
            except Exception as e:
                self.stats["last_error"] = str(e)
                logger.error(f"[FIRESTORE] Failed to sync order #{order_id}: {e}")
                return False

        logger.info(f"[FIRESTORE SIMULATION] Order #{order_id} captured in sync pipeline")
        return True

    def sync_reservation_to_firestore(self, reservation_dict: Dict[str, Any]) -> bool:
        """Syncs a table reservation to Cloud Firestore collection 'reservations'."""
        if not settings.FIREBASE_SYNC_ENABLED:
            return False

        res_id = str(reservation_dict.get("id"))
        self.stats["reservations_synced"] += 1
        import datetime
        self.stats["last_sync_timestamp"] = datetime.datetime.utcnow().isoformat()

        if self.is_live and self.db:
            try:
                doc_ref = self.db.collection("reservations").document(res_id)
                doc_ref.set(reservation_dict, merge=True)
                logger.info(f"[FIRESTORE] Synced Reservation #{res_id} to Cloud Firestore")
                return True
            except Exception as e:
                self.stats["last_error"] = str(e)
                logger.error(f"[FIRESTORE] Failed to sync reservation #{res_id}: {e}")
                return False

        logger.info(f"[FIRESTORE SIMULATION] Reservation #{res_id} captured in sync pipeline")
        return True

    def sync_review_to_firestore(self, review_dict: Dict[str, Any]) -> bool:
        """Syncs a guest review to Cloud Firestore collection 'reviews'."""
        if not settings.FIREBASE_SYNC_ENABLED:
            return False

        rev_id = str(review_dict.get("id"))
        self.stats["reviews_synced"] += 1
        import datetime
        self.stats["last_sync_timestamp"] = datetime.datetime.utcnow().isoformat()

        if self.is_live and self.db:
            try:
                doc_ref = self.db.collection("reviews").document(rev_id)
                doc_ref.set(review_dict, merge=True)
                logger.info(f"[FIRESTORE] Synced Review #{rev_id} to Cloud Firestore")
                return True
            except Exception as e:
                self.stats["last_error"] = str(e)
                logger.error(f"[FIRESTORE] Failed to sync review #{rev_id}: {e}")
                return False

        logger.info(f"[FIRESTORE SIMULATION] Review #{rev_id} captured in sync pipeline")
        return True

    def sync_menu_items_to_firestore(self, menu_items: List[Dict[str, Any]]) -> int:
        """Batch-syncs the complete culinary menu catalog to Cloud Firestore."""
        count = 0
        if self.is_live and self.db:
            try:
                batch = self.db.batch()
                for item in menu_items:
                    item_id = str(item.get("id"))
                    doc_ref = self.db.collection("menu_items").document(item_id)
                    batch.set(doc_ref, item, merge=True)
                    count += 1
                batch.commit()
                self.stats["menu_items_synced"] += count
                logger.info(f"[FIRESTORE] Successfully batch synced {count} menu items to Firestore")
                return count
            except Exception as e:
                self.stats["last_error"] = str(e)
                logger.error(f"[FIRESTORE] Batch menu sync error: {e}")
                return 0

        # Simulated batch count
        count = len(menu_items)
        self.stats["menu_items_synced"] += count
        return count


# Singleton instance
firebase_service = FirebaseService()
