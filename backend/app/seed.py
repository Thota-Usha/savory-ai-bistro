import json
from sqlalchemy.orm import Session
from app.models import User, MenuItem, Coupon, Review, Order, OrderItem, Reservation, IntegrityLog
from app.auth import hash_password

def seed_database(db: Session):
    # Check if already seeded
    if db.query(MenuItem).count() > 0:
        return

    print("Seeding database with Authentic Royal Telugu Cuisine & Rupee Pricing...")

    # 1. Users
    admin_user = User(
        name="Ustaad Ananda Rao (Executive Chef)",
        email="admin@savorybistro.com",
        hashed_password=hash_password("admin123"),
        role="admin",
        phone="+91 98480 22338",
        address="Banjara Hills, Road No. 12, Hyderabad, Telangana",
        dietary_preferences=json.dumps([])
    )
    demo_user = User(
        name="Lakshmi Sree",
        email="jane@example.com",
        hashed_password=hash_password("password123"),
        role="customer",
        phone="+91 94401 88291",
        address="Plot 42, Jubilee Hills, Hyderabad",
        dietary_preferences=json.dumps(["Peanut Allergy", "Non-Vegetarian Preferenced"])
    )
    db.add(admin_user)
    db.add(demo_user)
    db.commit()

    # 2. Coupons (in Indian Rupees)
    coupons = [
        Coupon(code="TELUGU20", discount_percent=20.0, max_discount=250.0, min_order=499.0, description="20% off your Royal Telugu feast (up to ₹250)"),
        Coupon(code="TASTE100", discount_percent=15.0, max_discount=100.0, min_order=399.0, description="Flat ₹100 reward on Biryanis & Curries"),
        Coupon(code="ROYAL50", discount_percent=25.0, max_discount=400.0, min_order=799.0, description="25% Grand Royal Banquet Discount")
    ]
    for c in coupons:
        db.add(c)
    db.commit()

    # 3. Authentic Telugu Gourmet Menu Items
    menu_items = [
        # Prarambha / Starters (Appetizers)
        MenuItem(
            name="Guntur Mirchi Bajji",
            category="Appetizers",
            description="Crisp gram-flour batter fried Bhavnagri green chilies, split and filled with crushed roasted peanuts, tangy allam-nimmakaya tamarind paste, and fresh chopped onions.",
            price=180.0,
            image="/images/guntur_mirchi_bajji.jpg",
            tags=json.dumps(["Vegetarian", "Spicy", "Chef Special"]),
            calories=320,
            prep_time="10-12 min",
            rating=4.9,
            reviews_count=210,
            allergens=json.dumps(["Peanuts"]),
            ingredients=json.dumps(["Bhavnagri Chilies", "Besan (Gram Flour)", "Tamarind", "Peanuts", "Ajwain"]),
            wine_pairing="Chilled Masala Majjiga or Sugandhi Nannari",
            is_available=True
        ),
        MenuItem(
            name="Andhra Kodi Vepudu (Pepper Chicken Fry)",
            category="Appetizers",
            description="Tender country chicken morsels dry-roasted on an iron skillet with crushed Guntur black peppercorns, caramelized shallots, fragrant curry leaves, and stone-ground garam masala.",
            price=360.0,
            image="/images/andhra_kodi_vepudu.jpg",
            tags=json.dumps(["Spicy", "High Protein", "Chef Special"]),
            calories=480,
            prep_time="15 min",
            rating=5.0,
            reviews_count=340,
            allergens=json.dumps([]),
            ingredients=json.dumps(["Farm Chicken", "Guntur Black Pepper", "Curry Leaves", "Shallots", "Pure Ghee"]),
            wine_pairing="Cold Bellam Panakam or Shiraz",
            is_available=True
        ),
        MenuItem(
            name="Royyala Vepudu (Godavari Spiced Prawn Fry)",
            category="Appetizers",
            description="Fresh coastal Godavari prawns flash-tossed in a spicy Andhra masala paste with garlic pods, slit green chilies, grated dry coconut, and freshly squeezed lemon juice.",
            price=420.0,
            image="/images/royyala_vepudu.jpg",
            tags=json.dumps(["Spicy", "High Protein"]),
            calories=410,
            prep_time="12-15 min",
            rating=4.9,
            reviews_count=180,
            allergens=json.dumps(["Crustacean Shellfish"]),
            ingredients=json.dumps(["Godavari Prawns", "Green Chilies", "Dry Coconut", "Curry Leaves", "Ginger-Garlic"]),
            wine_pairing="Sparkling Sugandhi Soda or Sauvignon Blanc",
            is_available=True
        ),
        MenuItem(
            name="Mokkajonna Garelu (Crispy Corn Vada)",
            category="Appetizers",
            description="Golden crunchy vadas handcrafted from sweet corn kernels, crushed cumin seeds, green chilies, fresh coriander, and ginger, served with piquant Allam Pachadi.",
            price=210.0,
            image="/images/mokkajonna_garelu.jpg",
            tags=json.dumps(["Vegetarian", "Gluten-Free"]),
            calories=290,
            prep_time="10 min",
            rating=4.8,
            reviews_count=145,
            allergens=json.dumps([]),
            ingredients=json.dumps(["Sweet Corn", "Cumin", "Allam (Ginger)", "Coriander", "Rice Flour"]),
            wine_pairing="Allam Tea or Filter Degree Coffee",
            is_available=True
        ),

        # Raja Ruchulu / Chef's Royal Signatures
        MenuItem(
            name="Hyderabadi Dum Biryani (Gosht / Mutton)",
            category="Chef Signatures",
            description="The pride of Deccan gastronomy. Long-grain aged Basmati rice layered with succulent young goat meat slow-cooked on dum in sealed clay handis with saffron, mint, and fried onions.",
            price=520.0,
            image="/images/hyderabadi_dum_biryani.jpg",
            tags=json.dumps(["Chef Special", "High Protein"]),
            calories=780,
            prep_time="20-25 min",
            rating=5.0,
            reviews_count=520,
            allergens=json.dumps(["Dairy"]),
            ingredients=json.dumps(["Tender Goat Meat", "Aged Basmati", "Pure Cow Ghee", "Kashmiri Saffron", "Mirchi Ka Salan"]),
            wine_pairing="Chilled Onion Raitha & Spiced Masala Majjiga",
            is_available=True
        ),
        MenuItem(
            name="Natu Kodi Pulusu (Country Chicken Curry)",
            category="Chef Signatures",
            description="Traditional Rayalaseema style country chicken stewed in an intensely aromatic, spicy red gravy crafted from stone-ground coriander, Guntur red chilies, and shallots.",
            price=460.0,
            image="/images/natu_kodi_pulusu.jpg",
            tags=json.dumps(["Spicy", "High Protein", "Chef Special"]),
            calories=640,
            prep_time="20 min",
            rating=4.9,
            reviews_count=290,
            allergens=json.dumps([]),
            ingredients=json.dumps(["Free-Range Country Chicken", "Guntur Mirchi", "Shallots", "Stone-ground Garam Masala"]),
            wine_pairing="Best paired with Steamed Bagara Rice or Garijalu",
            is_available=True
        ),
        MenuItem(
            name="Gongura Mamsam (Mutton with Sorrel Leaves)",
            category="Chef Signatures",
            description="Legendary Andhra delicacy featuring tender bone-in mutton slow-cooked with fresh sour Gongura (sorrel leaves), roasted red chilies, garlic cloves, and fragrant spices.",
            price=490.0,
            image="/images/gongura_mamsam.jpg",
            tags=json.dumps(["Chef Special", "Spicy", "High Protein"]),
            calories=690,
            prep_time="22 min",
            rating=5.0,
            reviews_count=310,
            allergens=json.dumps([]),
            ingredients=json.dumps(["Tender Goat Meat", "Fresh Gongura Leaves", "Red Chilies", "Garlic", "Mustard Oil"]),
            wine_pairing="Hot Steamed Sona Masoori Rice & Molten Ghee",
            is_available=True
        ),
        MenuItem(
            name="Nellore Chepala Pulusu (Claypot Fish Curry)",
            category="Chef Signatures",
            description="Fresh Korameenu (river murrel fish) simmered in an earthenware pot with ripe native tamarind, green mango slices, toasted fenugreek seeds, and aromatic tempering.",
            price=440.0,
            image="/images/nellore_chepala_pulusu.jpg",
            tags=json.dumps(["Chef Special", "Spicy"]),
            calories=480,
            prep_time="18-20 min",
            rating=4.9,
            reviews_count=225,
            allergens=json.dumps(["Fish"]),
            ingredients=json.dumps(["Korameenu (Murrel Fish)", "Raw Mango", "Nellore Tamarind", "Fenugreek", "Mustard"]),
            wine_pairing="Steamed Rice or Steamed Idlis",
            is_available=True
        ),

        # Kura & Sadham / Curries & Rice Specialties
        MenuItem(
            name="Gutti Vankaya Koora (Stuffed Brinjal Curry)",
            category="Artisanal Pastas & Mains",
            description="Tender purple baby eggplants stuffed with a royal paste of roasted peanuts, sesame seeds, dry coconut, and coriander seeds, simmered in a luscious onion-tamarind gravy.",
            price=320.0,
            image="/images/gutti_vankaya_koora.jpg",
            tags=json.dumps(["Vegetarian", "Chef Special"]),
            calories=460,
            prep_time="15 min",
            rating=4.9,
            reviews_count=280,
            allergens=json.dumps(["Peanuts", "Sesame"]),
            ingredients=json.dumps(["Baby Brinjal (Vankaya)", "Peanuts", "White Sesame", "Coconut", "Tamarind"]),
            wine_pairing="Bagara Rice or Jowar Roti (Jonna Rotte)",
            is_available=True
        ),
        MenuItem(
            name="Ulava Charu with Fresh Cream & Ghee",
            category="Artisanal Pastas & Mains",
            description="The crown jewel of Coastal Andhra. A thick, glossy reduction of slow-simmered horse gram infused with black peppercorns, cumin, and tamarind, crowned with homemade churned white butter.",
            price=290.0,
            image="/images/ulava_charu.jpg",
            tags=json.dumps(["Vegetarian", "Chef Special"]),
            calories=390,
            prep_time="12 min",
            rating=5.0,
            reviews_count=360,
            allergens=json.dumps(["Dairy"]),
            ingredients=json.dumps(["Horsegram (Ulavalu)", "Fresh Malai", "Tamarind", "Desi Ghee", "Black Pepper"]),
            wine_pairing="Hot Steamed Rice and Royyala Vepudu",
            is_available=True
        ),
        MenuItem(
            name="Gongura Pappu with Sona Masoori Rice",
            category="Artisanal Pastas & Mains",
            description="Creamy slow-boiled Kandipappu (toor dal) mashed with tender sorrel leaves, tempered generously in cow ghee with dry Byadagi red chilies, crushed garlic, mustard seeds, and hing.",
            price=260.0,
            image="/images/gongura_pappu.jpg",
            tags=json.dumps(["Vegetarian", "Gluten-Free"]),
            calories=420,
            prep_time="12 min",
            rating=4.8,
            reviews_count=195,
            allergens=json.dumps(["Dairy"]),
            ingredients=json.dumps(["Toor Dal", "Gongura Leaves", "Desi Ghee", "Garlic", "Cumin"]),
            wine_pairing="Papadum & Guntur Avakaya Pickle",
            is_available=True
        ),
        MenuItem(
            name="Avakaya Mudda Pappu Annam with Ghee",
            category="Artisanal Pastas & Mains",
            description="The quintessential Telugu comfort soul food. Piping hot Sona Masoori rice served with thick unseasoned yellow toor dal, fiery homemade Guntur mango Avakaya, and fragrant smoking hot cow ghee.",
            price=280.0,
            image="/images/avakaya_mudda_pappu.jpg",
            tags=json.dumps(["Vegetarian", "Spicy", "Chef Special"]),
            calories=510,
            prep_time="10 min",
            rating=5.0,
            reviews_count=420,
            allergens=json.dumps(["Dairy"]),
            ingredients=json.dumps(["Sona Masoori Rice", "Mudda Pappu", "Guntur Avakaya", "Pure Cow Ghee"]),
            wine_pairing="Chilled Masala Majjiga",
            is_available=True
        ),

        # Tiffins & Wood-Fired Hearth
        MenuItem(
            name="MLA Pesarattu with Upma & Allam Pachadi",
            category="Wood-Fired Hearth",
            description="Crisp whole green gram crepe stuffed with velvety ghee-roasted Bombay rava upma, finely chopped shallots and ginger, served with sweet-and-spicy Allam (ginger) chutney.",
            price=220.0,
            image="/images/mla_pesarattu.jpg",
            tags=json.dumps(["Vegetarian", "Chef Special"]),
            calories=440,
            prep_time="12 min",
            rating=4.9,
            reviews_count=270,
            allergens=json.dumps(["Gluten", "Dairy"]),
            ingredients=json.dumps(["Pesalu (Green Gram)", "Rava Upma", "Ginger Allam", "Desi Ghee", "Green Chilies"]),
            wine_pairing="Fresh Filter Coffee or Bellam Chai",
            is_available=True
        ),
        MenuItem(
            name="Guntur Karam Dosa with Neyyi (Ghee)",
            category="Wood-Fired Hearth",
            description="Paper-thin crispy fermented crepe generously slathered with fiery Guntur red chili-garlic paste, roasted gram dal podi, and bathed in golden cow ghee.",
            price=190.0,
            image="/images/guntur_karam_dosa.jpg",
            tags=json.dumps(["Vegetarian", "Spicy"]),
            calories=390,
            prep_time="10 min",
            rating=4.8,
            reviews_count=230,
            allergens=json.dumps(["Dairy"]),
            ingredients=json.dumps(["Fermented Dosa Batter", "Guntur Red Chili Paste", "Chana Dal Podi", "Cow Ghee"]),
            wine_pairing="Coconut Chutney & Sambar",
            is_available=True
        ),
        MenuItem(
            name="Rayalaseema Ragi Sangati with Ghee & Pulusu",
            category="Wood-Fired Hearth",
            description="Authentic steamed finger-millet mudda (ragi balls) paired with hot spicy Rayalaseema vegetable pulusu, roasted groundnut podi, and a generous dollop of pure A2 cow ghee.",
            price=240.0,
            image="/images/rayalaseema_ragi_sangati.jpg",
            tags=json.dumps(["Vegetarian", "Gluten-Free", "Chef Special"]),
            calories=380,
            prep_time="15 min",
            rating=4.9,
            reviews_count=210,
            allergens=json.dumps(["Dairy", "Peanuts"]),
            ingredients=json.dumps(["Finger Millet (Ragi)", "Broken Rice", "Tamarind", "Chili Spices", "Cow Ghee", "Groundnut Podi"]),
            wine_pairing="Masala Majjiga (Spiced Buttermilk)",
            is_available=True
        ),

        # Mithai / Decadent Desserts
        MenuItem(
            name="Authentic Atreyapuram Pootharekulu",
            category="Decadent Desserts",
            description="The legendary paper-thin rice starch 'paper sweet' from East Godavari, delicately folded with rich ghee, powdered organic jaggery, cardamom, and toasted pistachios.",
            price=210.0,
            image="/images/atreyapuram_pootharekulu.jpg",
            tags=json.dumps(["Vegetarian", "Chef Special"]),
            calories=310,
            prep_time="5 min",
            rating=5.0,
            reviews_count=410,
            allergens=json.dumps(["Dairy", "Nuts"]),
            ingredients=json.dumps(["Rice Starch Sheets", "Bellam (Jaggery)", "Desi Ghee", "Cardamom", "Pistachios"]),
            wine_pairing="Royal Badam Milk",
            is_available=True
        ),
        MenuItem(
            name="Kobbari Bobbatlu / Polelu with Ghee",
            category="Decadent Desserts",
            description="Melt-in-mouth handcrafted sweet flatbread stuffed with grated tender coconut, slow-cooked organic jaggery, and crushed green cardamom, served warm with molten ghee.",
            price=190.0,
            image="/images/kobbari_bobbatlu.jpg",
            tags=json.dumps(["Vegetarian"]),
            calories=360,
            prep_time="8 min",
            rating=4.9,
            reviews_count=215,
            allergens=json.dumps(["Gluten", "Dairy"]),
            ingredients=json.dumps(["Wheat Flour", "Grated Coconut", "Bellam (Jaggery)", "Cardamom", "Ghee"]),
            wine_pairing="Warm Saffron Milk",
            is_available=True
        ),
        MenuItem(
            name="Royal Hyderabadi Qubani Ka Meetha",
            category="Decadent Desserts",
            description="Traditional Nizami dessert made from stewed Turkish dried apricots simmered gently in light syrup with kewra essence, topped with thick clotted malai and almond kernels.",
            price=240.0,
            image="/images/qubani_ka_meetha.jpg",
            tags=json.dumps(["Vegetarian", "Chef Special"]),
            calories=420,
            prep_time="8 min",
            rating=5.0,
            reviews_count=350,
            allergens=json.dumps(["Dairy", "Nuts"]),
            ingredients=json.dumps(["Khubani (Apricots)", "Fresh Malai / Cream", "Apricot Kernels", "Kewra Essence"]),
            wine_pairing="Espresso or Filter Coffee",
            is_available=True
        ),
        MenuItem(
            name="Double Ka Meetha with Malai & Cashews",
            category="Decadent Desserts",
            description="Crisp golden bread triangles soaked in rich saffron and cardamom condensed milk rabri, garnished with toasted cashews, raisins, and edible silver vark.",
            price=220.0,
            image="/images/double_ka_meetha.jpg",
            tags=json.dumps(["Vegetarian"]),
            calories=480,
            prep_time="8 min",
            rating=4.8,
            reviews_count=180,
            allergens=json.dumps(["Dairy", "Gluten", "Nuts"]),
            ingredients=json.dumps(["Crisp Bread", "Condensed Milk Rabri", "Saffron", "Cashews", "Desi Ghee"]),
            wine_pairing="Masala Chai",
            is_available=True
        ),

        # Paanakam & Beverages
        MenuItem(
            name="Royal Bellam Panakam & Sugandhi Nannari",
            category="Artisanal Drinks",
            description="Ayurvedic nectar crafted from crushed palm jaggery, whole black pepper, dry ginger (sonth), green cardamom pods, and wild Nannari root extract over ice.",
            price=140.0,
            image="/images/royal_bellam_panakam.jpg",
            tags=json.dumps(["Vegan", "Gluten-Free", "Chef Special"]),
            calories=110,
            prep_time="4 min",
            rating=4.9,
            reviews_count=210,
            allergens=json.dumps([]),
            ingredients=json.dumps(["Organic Jaggery", "Nannari Roots", "Black Pepper", "Dry Ginger", "Cardamom"]),
            wine_pairing="Pairs exquisitely with fiery Kodi Vepudu and Biryani",
            is_available=True
        ),
        MenuItem(
            name="Masala Majjiga (Spiced Buttermilk)",
            category="Artisanal Drinks",
            description="Traditional earthen-pot churned curd blended with ginger, crushed green chilies, cilantro, curry leaves, hing, and roasted cumin rock salt.",
            price=110.0,
            image="/images/masala_majjiga.jpg",
            tags=json.dumps(["Vegetarian", "Gluten-Free"]),
            calories=75,
            prep_time="3 min",
            rating=4.9,
            reviews_count=320,
            allergens=json.dumps(["Dairy"]),
            ingredients=json.dumps(["Desi Churned Curd", "Allam (Ginger)", "Coriander", "Curry Leaves", "Jeera"]),
            wine_pairing="The perfect digestive cooler after spicy Gongura Mamsam",
            is_available=True
        ),
        MenuItem(
            name="Madras Filter Degree Coffee",
            category="Artisanal Drinks",
            description="Traditional south Indian degree decoction brewed in brass filters using plantation Peaberry coffee and chicory, frothed with foaming fresh cow milk.",
            price=120.0,
            image="/images/madras_filter_coffee.jpg",
            tags=json.dumps(["Vegetarian"]),
            calories=95,
            prep_time="4 min",
            rating=4.9,
            reviews_count=260,
            allergens=json.dumps(["Dairy"]),
            ingredients=json.dumps(["Peaberry Coffee Beans", "Chicory", "Boiled Cow Milk", "Organic Sugar"]),
            wine_pairing="Divine accompaniment for Pootharekulu or Bobbatlu",
            is_available=True
        )
    ]

    for m in menu_items:
        db.add(m)
    db.commit()

    # 4. Verified Customer Reviews (in Rupees & Telugu context)
    reviews = [
        Review(
            user_name="Srinivas Rao",
            user_avatar="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=150&q=80",
            rating=5,
            dish_name="Hyderabadi Dum Biryani (Gosht / Mutton)",
            comment="The Mutton Dum Biryani was sensational! Meat was falling off the bone and the aroma of pure ghee with saffron was royal. Best in town!",
            sentiment="Extremely Positive",
            verified_order=True,
            integrity_score=0.99,
            is_flagged=False
        ),
        Review(
            user_name="Padma Priya",
            user_avatar="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=150&q=80",
            rating=5,
            dish_name="Gongura Mamsam (Mutton with Sorrel Leaves)",
            comment="Authentic Guntur Gongura flavor! Perfectly tangy and spicy. The AI Sommelier paired it with Masala Majjiga, which balanced the spice amazingly.",
            sentiment="Extremely Positive",
            verified_order=True,
            integrity_score=0.98,
            is_flagged=False
        ),
        Review(
            user_name="Karthik Varma",
            user_avatar="https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=150&q=80",
            rating=5,
            dish_name="Authentic Atreyapuram Pootharekulu",
            comment="Pure Godavari nostalgia! The Pootharekulu was so delicate and filled with pure ghee and jaggery. Fast delivery and hygienic packaging.",
            sentiment="Positive",
            verified_order=True,
            integrity_score=0.97,
            is_flagged=False
        )
    ]
    for r in reviews:
        db.add(r)
    db.commit()

    # 5. Demo Order with Live Tracking Timeline
    demo_order = Order(
        user_id=demo_user.id,
        customer_name="Lakshmi Sree",
        customer_email="jane@example.com",
        customer_phone="+91 94401 88291",
        delivery_address="Plot 42, Jubilee Hills, Hyderabad",
        order_type="delivery",
        subtotal=740.0,
        tax=59.20,
        delivery_fee=49.00,
        discount=148.0,
        tip=50.0,
        total=700.20,
        coupon_code="TELUGU20",
        payment_method="UPI / GPay",
        status="out_for_delivery",
        tracking_timeline=json.dumps([
            {"status": "Order Placed", "timestamp": "2026-10-05T19:30:00.000Z", "detail": "Order verified via UPI. AI checked pricing & peanut allergen security."},
            {"status": "In Kitchen", "timestamp": "2026-10-05T19:33:00.000Z", "detail": "Ustaad Ananda Rao is assembling your Dum Biryani handi on coal."},
            {"status": "Quality Inspected", "timestamp": "2026-10-05T19:48:00.000Z", "detail": "Clay handi sealed and temperature integrity verified."},
            {"status": "Out for Delivery", "timestamp": "2026-10-05T19:54:00.000Z", "detail": "Rider Ramesh is on his way to Jubilee Hills (Est. 10 mins)."}
        ])
    )
    db.add(demo_order)
    db.commit()

    order_items = [
        OrderItem(
            order_id=demo_order.id,
            item_name="Hyderabadi Dum Biryani (Gosht / Mutton)",
            price=520.0,
            quantity=1,
            special_instructions="Extra Mirchi Ka Salan and fried onions",
            image="/images/hyderabadi_dum_biryani.jpg"
        ),
        OrderItem(
            order_id=demo_order.id,
            item_name="Masala Majjiga (Spiced Buttermilk)",
            price=110.0,
            quantity=2,
            special_instructions="Extra chilled",
            image="/images/masala_majjiga.jpg"
        )
    ]
    for oi in order_items:
        db.add(oi)
    db.commit()

    # 6. Demo Reservation
    demo_reservation = Reservation(
        user_id=demo_user.id,
        name="Lakshmi Sree",
        email="jane@example.com",
        phone="+91 94401 88291",
        date="2026-10-10",
        time="19:30",
        guests=4,
        area="Chef's Tasting Counter",
        special_requests="Family gathering, authentic spicy Andhra spices preferred.",
        status="confirmed"
    )
    db.add(demo_reservation)

    # 7. Initial Integrity Log
    init_log = IntegrityLog(
        event_type="system_initialization",
        severity="info",
        details=json.dumps({"message": "Telugu Culinary AI integrity engine active. Rupee currency and allergen thresholds operational."}),
        status="passed"
    )
    db.add(init_log)
    db.commit()

    print("Authentic Telugu Culinary Database seeding completed successfully!")
