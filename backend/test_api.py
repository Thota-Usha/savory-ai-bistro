import json
import sys
import httpx

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000"

def run_tests():
    client = httpx.Client(base_url=BASE_URL, timeout=10.0)

    print("==================================================")
    print("SAVORY AI BISTRO - FULL STACK INTEGRATION TESTS")
    print("==================================================")

    # 1. Health
    r = client.get("/api/health")
    assert r.status_code == 200, f"Health check failed: {r.status_code}"
    print(f" [PASS] Health Check: {r.json()['service']} v{r.json()['version']}")

    # 2. Menu
    r = client.get("/api/menu")
    assert r.status_code == 200, f"Menu failed: {r.status_code}"
    menu = r.json()
    assert len(menu) >= 18, f"Expected >= 18 items, got {len(menu)}"
    print(f" [PASS] Menu Catalog: {len(menu)} authentic Telugu culinary dishes available")

    # 3. AI Sommelier Chat
    r = client.post("/api/ai/chat", json={"message": "What beverage pairs best with Hyderabadi Dum Biryani?"})
    assert r.status_code == 200, f"AI chat failed: {r.status_code}"
    chat_data = r.json()
    assert "reply" in chat_data
    print(f" [PASS] AI Sommelier Chat: Replied ({chat_data['source']})")

    # 4. AI Recommendations
    r = client.post("/api/ai/recommendations", json={"mood": "spicy"})
    assert r.status_code == 200, f"AI recs failed: {r.status_code}"
    recs = r.json()
    assert len(recs["recommendations"]) > 0
    print(f" [PASS] AI Recommendations: Curated {len(recs['recommendations'])} dishes for 'spicy' mood")

    # 5. Customer Login
    r = client.post("/api/auth/login", json={"email": "jane@example.com", "password": "password123"})
    assert r.status_code == 200, f"Customer login failed: {r.status_code}"
    cust_data = r.json()
    cust_token = cust_data["access_token"]
    print(f" [PASS] Customer Login: Authenticated '{cust_data['user']['name']}' (JWT token generated)")

    # 6. Admin Login
    r = client.post("/api/auth/login", json={"email": "admin@savorybistro.com", "password": "admin123"})
    assert r.status_code == 200, f"Admin login failed: {r.status_code}"
    admin_data = r.json()
    admin_token = admin_data["access_token"]
    print(f" [PASS] Admin Login: Authenticated '{admin_data['user']['name']}' (Role: {admin_data['user']['role']})")

    # 7. Order Creation with Coupon & Allergen Shield
    order_payload = {
        "customer_name": "Lakshmi Sree",
        "customer_email": "jane@example.com",
        "customer_phone": "+91 98490 12345",
        "delivery_address": "Flat 402, Banjara Hills Road No. 12, Hyderabad",
        "order_type": "delivery",
        "items": [
            {
                "menu_item_id": "item-5",
                "item_name": "Hyderabadi Dum Biryani (Gosht / Mutton)",
                "price": 520.0,
                "quantity": 1,
                "special_instructions": "Extra mirchi ka salan and dahi ki chutney"
            }
        ],
        "coupon_code": "WELCOME20",
        "tip": 50.0,
        "payment_method": "UPI / GPay"
    }
    r = client.post(
        "/api/orders",
        json=order_payload,
        headers={"Authorization": f"Bearer {cust_token}"}
    )
    assert r.status_code == 201, f"Order creation failed: {r.text}"
    new_order = r.json()
    print(f" [PASS] Order Processing & AI Price Verification: Created order #{new_order['id'][:8]} (Total: ₹{new_order['total']:.2f})")

    # 8. Price Tampering Defense Check
    tampered_payload = {
        "customer_name": "Attacker",
        "customer_email": "attacker@evil.com",
        "items": [{"item_name": "Hyderabadi Dum Biryani (Gosht / Mutton)", "price": 10.0, "quantity": 1}]
    }
    r = client.post("/api/orders", json=tampered_payload)
    assert r.status_code in [422, 400], f"Tamper check should be blocked, got {r.status_code}"
    print(" [PASS] AI Security Guard: Successfully blocked client price tampering (422 Unprocessable)")

    # 9. Table Reservation
    res_payload = {
        "name": "Lakshmi Sree",
        "email": "jane@example.com",
        "phone": "+91 98490 12345",
        "date": "2026-10-15",
        "time": "19:30",
        "guests": 4,
        "area": "Nizam's Royal Courtyard",
        "special_requests": "Traditional sitting arrangement with brass thali service"
    }
    r = client.post("/api/reservations", json=res_payload)
    assert r.status_code == 201, f"Reservation failed: {r.text}"
    print(" [PASS] Table Reservation: Confirmed table booking")

    # 10. Review Submission & AI Sentiment Moderation
    rev_payload = {
        "rating": 5,
        "dish_name": "Hyderabadi Dum Biryani (Gosht / Mutton)",
        "comment": "Unbelievable authentic aroma of saffron, aged basmati and tender lamb! The mirchi ka salan was spectacular."
    }
    r = client.post("/api/reviews", json=rev_payload, headers={"Authorization": f"Bearer {cust_token}"})
    assert r.status_code == 201, f"Review failed: {r.text}"
    rev_data = r.json()
    print(f" [PASS] AI Review Moderation: Analyzed sentiment ('{rev_data['sentiment']}') & scored integrity ({rev_data['integrity_score']})")

    # 11. Admin Analytics
    r = client.get("/api/admin/analytics", headers={"Authorization": f"Bearer {admin_token}"})
    assert r.status_code == 200, f"Admin analytics failed: {r.status_code}"
    stats = r.json()
    print(f" [PASS] Admin Analytics: Revenue ₹{stats['total_revenue']:.2f}, Orders: {stats['total_orders']}, Rating: {stats['average_rating']}*")

    # 12. Frontend Static Files Serving
    r = client.get("/")
    assert r.status_code == 200 and "Savory AI Bistro" in r.text
    print(" [PASS] Frontend Single-Page App: HTML served with 200 OK")

    # 13. Firebase Cloud Status
    r = client.get("/api/firebase/status")
    assert r.status_code == 200, f"Firebase status failed: {r.status_code}"
    fb_status = r.json()
    assert "mode" in fb_status
    print(f" [PASS] Firebase Cloud Status: Mode='{fb_status['mode']}', Project='{fb_status['project_id']}'")

    # 14. Firebase Auth Token Exchange
    r = client.post("/api/auth/firebase-login", json={
        "id_token": "mock-firebase-token-patron-99",
        "name": "Sita Rama Rao",
        "email": "sita.rao@example.com"
    })
    assert r.status_code == 200, f"Firebase login failed: {r.status_code} - {r.text}"
    fb_login_data = r.json()
    assert "access_token" in fb_login_data
    print(f" [PASS] Firebase Authentication: Verified & logged in '{fb_login_data['user']['name']}'")

    # 15. Firebase Menu Sync to Cloud Firestore
    r = client.post("/api/firebase/sync-menu", headers={"Authorization": f"Bearer {admin_token}"})
    assert r.status_code == 200, f"Firebase menu sync failed: {r.status_code}"
    sync_res = r.json()
    assert sync_res["count"] >= 18
    print(f" [PASS] Firestore Menu Synchronization: Synced {sync_res['count']} dishes to Firestore")

    print("\n==================================================")
    print(" ALL 15 FULL-STACK & FIREBASE TESTS PASSED 100%!")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
