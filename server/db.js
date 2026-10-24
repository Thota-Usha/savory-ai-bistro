import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import bcrypt from 'bcryptjs';
import { initialMenuItems, initialReviews, initialCoupons } from './services/seedData.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const DATA_DIR = path.join(__dirname, 'data');
const DB_FILE = path.join(DATA_DIR, 'store.json');

// Ensure data folder exists
if (!fs.existsSync(DATA_DIR)) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
}

// Default initial state
function getDefaultState() {
  const salt = bcrypt.genSaltSync(10);
  const adminHash = bcrypt.hashSync('admin123', salt);
  const customerHash = bcrypt.hashSync('password123', salt);

  return {
    users: [
      {
        id: 'usr-admin-1',
        name: 'Executive Chef Alessandro',
        email: 'admin@savorybistro.com',
        password: adminHash,
        role: 'admin',
        phone: '+1 (555) 019-2834',
        address: '100 Culinary Way, Suite 400, Gourmet District',
        dietaryPreferences: [],
        createdAt: new Date().toISOString()
      },
      {
        id: 'usr-demo-1',
        name: 'Jane Doe',
        email: 'jane@example.com',
        password: customerHash,
        role: 'customer',
        phone: '+1 (555) 789-4321',
        address: '742 Evergreen Terrace, Apt 4B',
        dietaryPreferences: ['Nut Allergy', 'Gluten-Free Preferenced'],
        createdAt: new Date().toISOString()
      }
    ],
    menu: initialMenuItems,
    orders: [
      {
        id: 'ord-1001',
        userId: 'usr-demo-1',
        customerName: 'Jane Doe',
        customerEmail: 'jane@example.com',
        customerPhone: '+1 (555) 789-4321',
        deliveryAddress: '742 Evergreen Terrace, Apt 4B',
        orderType: 'delivery',
        items: [
          {
            id: 'item-4',
            name: 'Prime Wagyu Filet Mignon',
            price: 58.0,
            quantity: 1,
            specialInstructions: 'Medium-rare, extra demi-glace on the side',
            image: 'https://images.unsplash.com/photo-1558030006-450675393462?auto=format&fit=crop&w=800&q=80'
          },
          {
            id: 'item-16',
            name: 'Smoked Rosemary Old Fashioned',
            price: 17.0,
            quantity: 2,
            specialInstructions: '',
            image: 'https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?auto=format&fit=crop&w=800&q=80'
          }
        ],
        subtotal: 92.0,
        tax: 7.36,
        deliveryFee: 4.99,
        discount: 18.4,
        tip: 15.0,
        total: 100.95,
        couponCode: 'WELCOME20',
        paymentMethod: 'Credit Card (**** 4242)',
        status: 'out_for_delivery',
        trackingTimeline: [
          { status: 'Order Placed', timestamp: '2026-10-05T19:30:00.000Z', detail: 'Order verified & payment authorized' },
          { status: 'In Kitchen', timestamp: '2026-10-05T19:33:00.000Z', detail: 'Chef Alessandro is searing Wagyu' },
          { status: 'Quality Inspected', timestamp: '2026-10-05T19:48:00.000Z', detail: 'Temperature & allergen integrity confirmed' },
          { status: 'Out for Delivery', timestamp: '2026-10-05T19:54:00.000Z', detail: 'Courier David is on the way (Est. 8 mins)' }
        ],
        createdAt: '2026-10-05T19:30:00.000Z'
      }
    ],
    reservations: [
      {
        id: 'res-501',
        userId: 'usr-demo-1',
        name: 'Jane Doe',
        email: 'jane@example.com',
        phone: '+1 (555) 789-4321',
        date: '2026-10-08',
        time: '19:30',
        guests: 2,
        area: "Chef's Tasting Counter",
        specialRequests: 'Anniversary celebration, window or quiet view preferred.',
        status: 'confirmed',
        createdAt: new Date().toISOString()
      }
    ],
    reviews: initialReviews,
    coupons: initialCoupons,
    inquiries: [
      {
        id: 'inq-1',
        name: 'Michael Sterling',
        email: 'm.sterling@events.org',
        phone: '+1 (555) 987-1234',
        subject: 'Private Dining & Corporate Tasting Event',
        message: 'We are seeking to host a private 25-person tasting menu for executive guests next month. Do you offer custom sommelier pairings?',
        integrityCheckResult: { passed: true, score: 0.99, flag: 'clean' },
        status: 'unread',
        createdAt: new Date().toISOString()
      }
    ],
    integrityLogs: [
      {
        id: 'log-1',
        timestamp: new Date().toISOString(),
        eventType: 'system_initialization',
        severity: 'info',
        details: { message: 'AI integrity engine initialized with baseline safety thresholds.' },
        status: 'passed'
      }
    ]
  };
}

// In-memory cache synced with disk
let db = null;

function loadDB() {
  if (db) return db;
  try {
    if (fs.existsSync(DB_FILE)) {
      const raw = fs.readFileSync(DB_FILE, 'utf-8');
      db = JSON.parse(raw);
    } else {
      db = getDefaultState();
      saveDB();
    }
  } catch (err) {
    console.error('Error loading DB file, fallback to default state:', err);
    db = getDefaultState();
  }
  return db;
}

function saveDB() {
  try {
    if (db) {
      fs.writeFileSync(DB_FILE, JSON.stringify(db, null, 2), 'utf-8');
    }
  } catch (err) {
    console.error('Error saving DB to disk:', err);
  }
}

// Data Access Methods
export const DB = {
  // Users
  getUsers: () => loadDB().users,
  findUserByEmail: (email) => loadDB().users.find((u) => u.email.toLowerCase() === email.toLowerCase()),
  findUserById: (id) => loadDB().users.find((u) => u.id === id),
  createUser: (userData) => {
    const database = loadDB();
    database.users.push(userData);
    saveDB();
    return userData;
  },
  updateUser: (id, updates) => {
    const database = loadDB();
    const idx = database.users.findIndex((u) => u.id === id);
    if (idx !== -1) {
      database.users[idx] = { ...database.users[idx], ...updates };
      saveDB();
      return database.users[idx];
    }
    return null;
  },

  // Menu
  getMenuItems: () => loadDB().menu,
  getMenuItemById: (id) => loadDB().menu.find((m) => m.id === id),
  createMenuItem: (item) => {
    const database = loadDB();
    database.menu.unshift(item);
    saveDB();
    return item;
  },
  updateMenuItem: (id, updates) => {
    const database = loadDB();
    const idx = database.menu.findIndex((m) => m.id === id);
    if (idx !== -1) {
      database.menu[idx] = { ...database.menu[idx], ...updates };
      saveDB();
      return database.menu[idx];
    }
    return null;
  },
  deleteMenuItem: (id) => {
    const database = loadDB();
    const idx = database.menu.findIndex((m) => m.id === id);
    if (idx !== -1) {
      const removed = database.menu.splice(idx, 1)[0];
      saveDB();
      return removed;
    }
    return null;
  },

  // Orders
  getOrders: () => loadDB().orders,
  getOrderById: (id) => loadDB().orders.find((o) => o.id === id),
  getUserOrders: (userId) => loadDB().orders.filter((o) => o.userId === userId),
  createOrder: (order) => {
    const database = loadDB();
    database.orders.unshift(order);
    saveDB();
    return order;
  },
  updateOrderStatus: (id, status, timelineEntry = null) => {
    const database = loadDB();
    const order = database.orders.find((o) => o.id === id);
    if (order) {
      order.status = status;
      if (timelineEntry) {
        order.trackingTimeline.push(timelineEntry);
      }
      saveDB();
      return order;
    }
    return null;
  },

  // Reservations
  getReservations: () => loadDB().reservations,
  getUserReservations: (userId) => loadDB().reservations.filter((r) => r.userId === userId),
  createReservation: (res) => {
    const database = loadDB();
    database.reservations.unshift(res);
    saveDB();
    return res;
  },
  updateReservationStatus: (id, status) => {
    const database = loadDB();
    const res = database.reservations.find((r) => r.id === id);
    if (res) {
      res.status = status;
      saveDB();
      return res;
    }
    return null;
  },

  // Reviews
  getReviews: () => loadDB().reviews,
  createReview: (review) => {
    const database = loadDB();
    database.reviews.unshift(review);
    saveDB();
    return review;
  },

  // Inquiries
  getInquiries: () => loadDB().inquiries,
  createInquiry: (inq) => {
    const database = loadDB();
    database.inquiries.unshift(inq);
    saveDB();
    return inq;
  },
  updateInquiryStatus: (id, status) => {
    const database = loadDB();
    const inq = database.inquiries.find((i) => i.id === id);
    if (inq) {
      inq.status = status;
      saveDB();
      return inq;
    }
    return null;
  },

  // Coupons
  getCoupons: () => loadDB().coupons,
  findCoupon: (code) => {
    if (!code) return null;
    return loadDB().coupons.find((c) => c.code.toUpperCase() === code.trim().toUpperCase());
  },

  // Integrity & Security Logs
  getIntegrityLogs: () => loadDB().integrityLogs,
  logIntegrityEvent: (event) => {
    const database = loadDB();
    const entry = {
      id: `log-${Date.now()}-${Math.floor(Math.random() * 1000)}`,
      timestamp: new Date().toISOString(),
      ...event
    };
    database.integrityLogs.unshift(entry);
    // Keep max 200 logs
    if (database.integrityLogs.length > 200) {
      database.integrityLogs = database.integrityLogs.slice(0, 200);
    }
    saveDB();
    return entry;
  }
};
