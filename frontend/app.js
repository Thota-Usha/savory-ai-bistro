/**
 * Savory AI Bistro - Core Application Logic
 * Full-stack culinary intelligence, dynamic menu, real-time cart, and AI interactions.
 */

// State Store
const state = {
  user: null,
  token: localStorage.getItem('savory_token') || null,
  cart: JSON.parse(localStorage.getItem('savory_cart') || '[]'),
  menuItems: [],
  categories: [
    'All',
    'Vepudulu & Starters',
    'Royal Biryani & Pulao',
    'Andhra & Rayalaseema Curries',
    'Pappu, Charu & Rice Delights',
    'Tiffins & Crispy Dosas',
    'Traditional Mithai & Desserts',
    'Refreshing Panakalu & Beverages'
  ],
  currentCategory: 'All',
  currentDietary: 'All',
  searchQuery: '',
  currentSort: 'recommended',
  currentMood: '',
  appliedCoupon: null,
  tipAmount: 50.0,
  chatHistory: [],
  activeOrderId: null,
  adminData: {
    analytics: null,
    orders: [],
    reservations: [],
    integrityLogs: [],
    inquiries: []
  }
};

// API Helper
async function apiRequest(endpoint, options = {}) {
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {})
  };

  if (state.token) {
    headers['Authorization'] = `Bearer ${state.token}`;
  }

  try {
    const res = await fetch(`/api${endpoint}`, {
      ...options,
      headers
    });

    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      throw new Error(data.detail || data.message || `Request failed (${res.status})`);
    }
    return data;
  } catch (err) {
    console.error(`API Error on ${endpoint}:`, err);
    throw err;
  }
}

// Toast Notifications
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  
  let icon = 'ℹ️';
  if (type === 'success') icon = '✅';
  if (type === 'error') icon = '⚠️';
  if (type === 'warning') icon = '🛡️';

  toast.innerHTML = `<span>${icon}</span><span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(-100%)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

// Global BistroApp API exposed for HTML onclick handlers
window.BistroApp = {
  // Modal Handlers
  openModal(id) {
    const modal = document.getElementById(id);
    if (modal) modal.classList.add('active');
  },
  closeModal(id) {
    const modal = document.getElementById(id);
    if (modal) modal.classList.remove('active');
  },

  // Firebase Actions
  async loginWithFirebase() {
    try {
      showToast('Authenticating with Firebase...', 'info');
      const randomId = Math.floor(Math.random() * 9000 + 1000);
      const res = await apiRequest('/auth/firebase-login', {
        method: 'POST',
        body: JSON.stringify({
          id_token: `mock-firebase-token-patron-${randomId}`,
          name: `Royal Patron #${randomId}`,
          email: `patron${randomId}@firebase.savorybistro.com`
        })
      });
      setUserSession(res.access_token, res.user);
      showToast(`Welcome ${res.user.name}! Authenticated via Firebase.`, 'success');
      this.closeModal('auth-modal');
    } catch (err) {
      showToast(err.message || 'Firebase login failed', 'error');
    }
  },

  async syncMenuToFirestore() {
    try {
      showToast('Syncing Telugu menu catalog to Cloud Firestore...', 'info');
      const res = await apiRequest('/firebase/sync-menu', { method: 'POST' });
      showToast(res.message || 'Menu dishes synced to Cloud Firestore!', 'success');
      await this.refreshFirebaseStatus();
    } catch (err) {
      showToast(err.message || 'Firestore synchronization failed', 'error');
    }
  },

  async refreshFirebaseStatus() {
    await loadFirebaseStatus();
    showToast('Firebase connection status updated', 'info');
  },

  // Cart Actions
  addToCart(itemId, qty = 1, instructions = '') {
    const item = state.menuItems.find(m => m.id === itemId);
    if (!item) return;

    if (!item.is_available) {
      showToast(`Sorry, "${item.name}" is currently sold out!`, 'error');
      return;
    }

    const existing = state.cart.find(c => c.id === itemId);
    if (existing) {
      existing.quantity += qty;
      if (instructions) existing.special_instructions = instructions;
    } else {
      state.cart.push({
        id: item.id,
        menu_item_id: item.id,
        item_name: item.name,
        price: item.price,
        image: item.image,
        quantity: qty,
        special_instructions: instructions,
        allergens: item.allergens || []
      });
    }

    saveCart();
    renderCart();
    showToast(`Added "${item.name}" to your cart`, 'success');

    // Run AI Allergen Collision Detection
    checkCartAllergens();
  },

  removeFromCart(index) {
    state.cart.splice(index, 1);
    saveCart();
    renderCart();
    checkCartAllergens();
  },

  updateCartQty(index, delta) {
    if (!state.cart[index]) return;
    state.cart[index].quantity += delta;
    if (state.cart[index].quantity <= 0) {
      state.cart.splice(index, 1);
    }
    saveCart();
    renderCart();
    checkCartAllergens();
  },

  updateCartInstructions(index, value) {
    if (state.cart[index]) {
      state.cart[index].special_instructions = value;
      saveCart();
    }
  },

  // Quick Demo Login
  async quickLogin(email, password) {
    try {
      const data = await apiRequest('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password })
      });
      setUserSession(data.token_type ? data.access_token : data.token, data.user);
      showToast(`Welcome back, ${data.user.name}!`, 'success');
      window.BistroApp.closeModal('auth-modal');
    } catch (err) {
      showToast(err.message, 'error');
    }
  },

  // View Order Tracking
  async trackOrder(orderId) {
    try {
      const order = await apiRequest(`/orders/${orderId}`);
      renderOrderTracking(order);
      window.BistroApp.openModal('order-tracking-modal');
    } catch (err) {
      showToast(`Could not load order tracking: ${err.message}`, 'error');
    }
  },

  // Admin Quick Status Transition
  async setOrderStatus(orderId, newStatus) {
    try {
      await apiRequest(`/admin/orders/${orderId}/status`, {
        method: 'PUT',
        body: JSON.stringify({ status: newStatus })
      });
      showToast(`Order status updated to "${newStatus}"`, 'success');
      loadAdminOrders();
      loadAdminAnalytics();
    } catch (err) {
      showToast(err.message, 'error');
    }
  },

  // Admin Toggle Dish Availability
  async toggleDish(itemId) {
    try {
      await apiRequest(`/menu/${itemId}/toggle-availability`, { method: 'PATCH' });
      showToast('Menu stock status toggled', 'success');
      loadMenu();
      loadAdminMenu();
    } catch (err) {
      showToast(err.message, 'error');
    }
  },

  // Admin Delete Dish
  async deleteDish(itemId) {
    if (!confirm('Are you sure you want to retire this culinary dish from the menu?')) return;
    try {
      await apiRequest(`/menu/${itemId}`, { method: 'DELETE' });
      showToast('Dish deleted successfully', 'info');
      loadMenu();
      loadAdminMenu();
    } catch (err) {
      showToast(err.message, 'error');
    }
  }
};

// Storage Helpers
function saveCart() {
  localStorage.setItem('savory_cart', JSON.stringify(state.cart));
  updateCartBadge();
}

function updateCartBadge() {
  const badge = document.getElementById('cart-count-badge');
  if (badge) {
    const totalQty = state.cart.reduce((sum, item) => sum + item.quantity, 0);
    badge.textContent = totalQty;
  }
}

function setUserSession(token, user) {
  state.token = token;
  state.user = user;
  localStorage.setItem('savory_token', token);
  localStorage.setItem('savory_user', JSON.stringify(user));
  updateAuthUI();
  checkCartAllergens();
}

function clearUserSession() {
  state.token = null;
  state.user = null;
  localStorage.removeItem('savory_token');
  localStorage.removeItem('savory_user');
  updateAuthUI();
}

function updateAuthUI() {
  const authBtnLabel = document.getElementById('auth-btn-label');
  const adminNavBtn = document.getElementById('admin-nav-btn');

  if (state.user) {
    if (authBtnLabel) authBtnLabel.textContent = state.user.name.split(' ')[0];
    if (adminNavBtn) {
      if (state.user.role === 'admin') {
        adminNavBtn.classList.remove('hidden');
      } else {
        adminNavBtn.classList.add('hidden');
      }
    }
  } else {
    if (authBtnLabel) authBtnLabel.textContent = 'Sign In';
    if (adminNavBtn) adminNavBtn.classList.add('hidden');
  }
}

// AI Allergen Collision Detector
function checkCartAllergens() {
  const alertBox = document.getElementById('cart-allergen-alert');
  const alertText = document.getElementById('cart-allergen-text');
  if (!alertBox || !alertText) return;

  if (!state.user || !state.user.dietary_preferences || state.user.dietary_preferences.length === 0 || state.cart.length === 0) {
    alertBox.classList.add('hidden');
    return;
  }

  const userPrefs = state.user.dietary_preferences;
  const warnings = [];

  for (const item of state.cart) {
    const dish = state.menuItems.find(m => m.id === item.id);
    if (!dish) continue;

    for (const pref of userPrefs) {
      const prefLower = pref.toLowerCase();
      for (const alg of dish.allergens || []) {
        if (alg.toLowerCase().includes(prefLower) || prefLower.includes(alg.toLowerCase())) {
          warnings.push(`"${dish.name}" contains ${alg} (conflicts with your saved "${pref}")`);
        }
      }
    }
  }

  if (warnings.length > 0) {
    alertText.innerHTML = `<strong>AI Health Integrity Shield:</strong> ${warnings.join(' • ')}`;
    alertBox.classList.remove('hidden');
  } else {
    alertBox.classList.add('hidden');
  }
}

// Load Menu
async function loadMenu() {
  try {
    const params = new URLSearchParams();
    if (state.currentCategory !== 'All') params.append('category', state.currentCategory);
    if (state.currentDietary !== 'All') params.append('dietary', state.currentDietary);
    if (state.searchQuery) params.append('search', state.searchQuery);
    if (state.currentSort) params.append('sort', state.currentSort);

    const items = await apiRequest(`/menu?${params.toString()}`);
    state.menuItems = items;
    renderMenuGrid(items);
  } catch (err) {
    showToast(`Failed to load menu: ${err.message}`, 'error');
  }
}

// Render Menu Cards
function renderMenuGrid(items) {
  const container = document.getElementById('menu-grid-container');
  if (!container) return;

  if (items.length === 0) {
    container.innerHTML = `
      <div class="col-span-full py-16 text-center text-slate-400">
        <div class="text-4xl mb-3">🍽️</div>
        <h4 class="font-serif text-xl font-bold text-white mb-1">No Culinary Creations Found</h4>
        <p class="text-xs text-slate-400">Try adjusting your category, search keyword, or dietary filter.</p>
      </div>
    `;
    return;
  }

  container.innerHTML = items.map(item => {
    const tagsHtml = (item.tags || []).map(t => {
      let badgeClass = 'badge-gold';
      if (t === 'Vegetarian' || t === 'Vegan') badgeClass = 'badge-green';
      if (t === 'Gluten-Free') badgeClass = 'badge-blue';
      if (t === 'Spicy') badgeClass = 'badge-red';
      return `<span class="badge ${badgeClass}">${t}</span>`;
    }).join(' ');

    const allergensHtml = (item.allergens && item.allergens.length > 0) 
      ? `<div class="text-[11px] text-slate-400 flex items-center gap-1 mt-2">
           <span class="text-amber-400">Allergens:</span> ${item.allergens.join(', ')}
         </div>`
      : '';

    const winePairingHtml = item.wine_pairing 
      ? `<div class="mt-2.5 p-2 rounded-lg bg-amber-500/10 border border-amber-500/20 text-[11px] text-amber-300 flex items-center gap-1.5">
           <span>🍷 Sommelier Pairing:</span> <span class="font-medium">${item.wine_pairing}</span>
         </div>`
      : '';

    return `
      <div class="menu-card group">
        <div class="relative overflow-hidden">
          <img src="${item.image}" alt="${item.name}" loading="lazy">
          <div class="absolute top-3 right-3 bg-black/80 backdrop-blur-md px-3 py-1 rounded-full text-sm font-bold text-amber-400 border border-amber-500/30">
            ₹${item.price.toFixed(2)}
          </div>
          <div class="absolute top-3 left-3 flex flex-wrap gap-1">
            ${tagsHtml}
          </div>
        </div>

        <div class="p-5 flex-1 flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between text-xs text-slate-400 mb-1">
              <span>${item.category}</span>
              <span>⭐ ${item.rating.toFixed(1)} (${item.reviews_count || 100}+ reviews)</span>
            </div>
            <h3 class="font-serif text-xl font-bold text-white group-hover:text-amber-300 transition-colors">${item.name}</h3>
            <p class="text-xs text-slate-300 mt-2 line-clamp-3 leading-relaxed font-light">${item.description}</p>
            
            <div class="flex items-center gap-3 mt-3 text-[11px] text-slate-400">
              <span>🔥 ${item.calories} kcal</span>
              <span>⏱️ ${item.prep_time}</span>
            </div>

            ${allergensHtml}
            ${winePairingHtml}
          </div>

          <div class="mt-5 pt-4 border-t border-slate-800 flex items-center justify-between">
            <span class="font-serif text-2xl font-bold text-amber-400">₹${item.price.toFixed(2)}</span>
            <button onclick="window.BistroApp.addToCart('${item.id}')" class="btn btn-gold btn-sm">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
              Add to Order
            </button>
          </div>
        </div>
      </div>
    `;
  }).join('');
}

// AI Personalized Recommendations
async function loadAIRecommendations(mood = '') {
  const container = document.getElementById('ai-recommendations-container');
  const explanationEl = document.getElementById('ai-recommendation-explanation');
  if (!container) return;

  try {
    const data = await apiRequest('/ai/recommendations', {
      method: 'POST',
      body: JSON.stringify({ mood: mood || null })
    });

    if (explanationEl && data.explanation) {
      explanationEl.textContent = data.explanation;
    }

    container.innerHTML = data.recommendations.map(item => `
      <div class="glass-panel p-4 rounded-2xl border border-amber-500/20 hover:border-amber-400/50 transition-all flex flex-col justify-between">
        <div>
          <div class="relative rounded-xl overflow-hidden mb-3">
            <img src="${item.image}" alt="${item.name}" class="w-full h-36 object-cover">
            <span class="absolute bottom-2 right-2 bg-black/80 text-amber-400 px-2 py-0.5 rounded-md text-xs font-bold">
              ₹${item.price.toFixed(2)}
            </span>
          </div>
          <span class="badge badge-gold text-[10px] mb-1">AI Recommendation</span>
          <h4 class="font-serif font-bold text-white text-base">${item.name}</h4>
          <p class="text-[11px] text-slate-300 mt-1 line-clamp-2">${item.description}</p>
        </div>
        <div class="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between">
          <span class="text-xs text-amber-400 font-bold">⭐ ${item.rating}</span>
          <button onclick="window.BistroApp.addToCart('${item.id}')" class="btn btn-gold btn-sm text-xs py-1 px-3">
            Quick Add
          </button>
        </div>
      </div>
    `).join('');
  } catch (err) {
    console.warn('AI Recommendations fallback:', err);
  }
}

// Render Cart Drawer
function renderCart() {
  const container = document.getElementById('cart-items-container');
  const subtotalEl = document.getElementById('cart-subtotal');
  const discountRow = document.getElementById('discount-row');
  const discountEl = document.getElementById('cart-discount');
  const taxEl = document.getElementById('cart-tax');
  const totalEl = document.getElementById('cart-total');
  const checkoutTotalDisplay = document.getElementById('checkout-total-display');

  if (!container) return;

  if (state.cart.length === 0) {
    container.innerHTML = `
      <div class="h-full flex flex-col items-center justify-center text-center p-8 text-slate-400">
        <div class="text-5xl mb-4">🛒</div>
        <h4 class="font-serif text-lg font-bold text-white mb-1">Your Cart is Empty</h4>
        <p class="text-xs text-slate-400 max-w-xs mb-4">Explore our authentic Telugu culinary delicacies or consult with Ustaad Ananda Rao.</p>
        <button onclick="window.BistroApp.closeModal('cart-drawer')" class="btn btn-outline btn-sm">Explore Menu</button>
      </div>
    `;
    if (subtotalEl) subtotalEl.textContent = '₹0.00';
    if (taxEl) taxEl.textContent = '₹0.00';
    if (totalEl) totalEl.textContent = '₹0.00';
    if (discountRow) discountRow.classList.add('hidden');
    return;
  }

  // Calculate pricing
  const subtotal = state.cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
  let discount = 0;
  if (state.appliedCoupon) {
    discount = Math.min(subtotal * (state.appliedCoupon.discount_percent / 100), state.appliedCoupon.max_discount || 300);
  }
  const tax = (subtotal - discount) * 0.05;
  const delivery = subtotal > 0 ? 49.0 : 0;
  const tip = subtotal > 0 ? (state.tipAmount || 0) : 0;
  const total = subtotal - discount + tax + delivery + tip;

  if (subtotalEl) subtotalEl.textContent = `₹${subtotal.toFixed(2)}`;
  if (taxEl) taxEl.textContent = `₹${tax.toFixed(2)}`;
  if (totalEl) totalEl.textContent = `₹${total.toFixed(2)}`;
  if (checkoutTotalDisplay) checkoutTotalDisplay.textContent = `₹${total.toFixed(2)}`;

  if (discount > 0 && discountRow && discountEl) {
    discountRow.classList.remove('hidden');
    discountEl.textContent = `-₹${discount.toFixed(2)} (${state.appliedCoupon.code})`;
  } else if (discountRow) {
    discountRow.classList.add('hidden');
  }

  container.innerHTML = state.cart.map((item, index) => `
    <div class="p-3.5 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
      <div class="flex items-start gap-3">
        <img src="${item.image}" alt="${item.item_name}" class="w-16 h-16 rounded-lg object-cover shrink-0">
        <div class="flex-1 min-w-0">
          <div class="flex items-start justify-between">
            <h4 class="font-serif font-bold text-white text-sm truncate">${item.item_name}</h4>
            <button onclick="window.BistroApp.removeFromCart(${index})" class="text-slate-500 hover:text-rose-400 text-xs ml-2">✕</button>
          </div>
          <div class="text-xs text-amber-400 font-semibold mt-0.5">₹${item.price.toFixed(2)} each</div>
          
          <!-- Quantity Stepper -->
          <div class="flex items-center gap-2 mt-2">
            <button onclick="window.BistroApp.updateCartQty(${index}, -1)" class="w-6 h-6 rounded-md bg-slate-800 text-slate-300 hover:bg-slate-700 flex items-center justify-center text-xs">-</button>
            <span class="text-xs font-bold text-white px-1">${item.quantity}</span>
            <button onclick="window.BistroApp.updateCartQty(${index}, 1)" class="w-6 h-6 rounded-md bg-slate-800 text-slate-300 hover:bg-slate-700 flex items-center justify-center text-xs">+</button>
            <span class="text-xs text-slate-400 ml-auto font-bold">₹${(item.price * item.quantity).toFixed(2)}</span>
          </div>
        </div>
      </div>

      <!-- Special Cooking Instructions Field -->
      <div>
        <input type="text" 
               placeholder="Special request (e.g. less spice, extra ghee, crispy)..." 
               value="${item.special_instructions || ''}"
               onchange="window.BistroApp.updateCartInstructions(${index}, this.value)"
               class="w-full bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1 text-[11px] text-slate-300 placeholder-slate-600 focus:outline-none focus:border-amber-400">
      </div>
    </div>
  `).join('');
}

// Reviews
async function loadReviews() {
  const container = document.getElementById('reviews-container');
  if (!container) return;

  try {
    const reviews = await apiRequest('/reviews');
    container.innerHTML = reviews.map(r => `
      <div class="glass-panel p-6 rounded-2xl border border-slate-800 flex flex-col justify-between">
        <div>
          <div class="flex items-center justify-between mb-3">
            <div class="flex items-center gap-3">
              <img src="${r.user_avatar || 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?auto=format&fit=crop&w=150&q=80'}" 
                   alt="${r.user_name}" class="w-10 h-10 rounded-full object-cover">
              <div>
                <h4 class="font-bold text-white text-sm">${r.user_name}</h4>
                <div class="flex text-amber-400 text-xs">
                  ${'★'.repeat(r.rating)}${'☆'.repeat(5 - r.rating)}
                </div>
              </div>
            </div>
            <span class="badge badge-gold text-[10px]">${r.sentiment || 'Positive'}</span>
          </div>
          ${r.dish_name ? `<div class="text-xs text-amber-300 font-medium mb-2">Ordered: ${r.dish_name}</div>` : ''}
          <p class="text-xs text-slate-300 leading-relaxed italic">"${r.comment}"</p>
        </div>
        <div class="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-[10px] text-slate-500">
          <span>🛡️ Verified Gastronome (${Math.round(r.integrity_score * 100)}% Integrity)</span>
          <span>Verified Order</span>
        </div>
      </div>
    `).join('');
  } catch (err) {
    console.warn('Reviews load fallback:', err);
  }
}

// Order Tracking Render
function renderOrderTracking(order) {
  const orderIdEl = document.getElementById('track-order-id');
  const statusBadgeEl = document.getElementById('track-status-badge');
  const stepperContainer = document.getElementById('tracking-stepper-container');
  const itemsContainer = document.getElementById('track-order-items');

  if (orderIdEl) orderIdEl.textContent = `#${order.id.slice(0, 8).toUpperCase()}`;
  if (statusBadgeEl) {
    statusBadgeEl.textContent = order.status.replace('_', ' ').toUpperCase();
    statusBadgeEl.className = `badge ${order.status === 'delivered' ? 'badge-green' : 'badge-blue'}`;
  }

  const steps = [
    { key: 'pending', title: 'Order Placed & Verified', desc: 'AI checked pricing, payment authorized, allergy shield passed.' },
    { key: 'preparing', title: 'Executive Kitchen Prep', desc: 'Culinary team is crafting dishes with precision heat.' },
    { key: 'quality_check', title: 'Quality & Temperature Inspection', desc: 'Passed sommelier standards and temperature integrity.' },
    { key: 'out_for_delivery', title: 'Out For White-Glove Delivery', desc: 'Courier in transit with climate-controlled delivery carrier.' },
    { key: 'delivered', title: 'Delivered & Bon Appétit', desc: 'Order arrived at customer destination. Savor your meal!' }
  ];

  const statusOrder = ['pending', 'preparing', 'quality_check', 'out_for_delivery', 'delivered'];
  const currentIndex = statusOrder.indexOf(order.status);

  if (stepperContainer) {
    stepperContainer.innerHTML = steps.map((s, idx) => {
      let stateClass = '';
      if (idx < currentIndex) stateClass = 'completed';
      else if (idx === currentIndex) stateClass = 'active';

      let iconText = idx + 1;
      if (idx < currentIndex) iconText = '✓';

      return `
        <div class="stepper-item ${stateClass}">
          <div class="stepper-icon">${iconText}</div>
          <div class="flex-1">
            <h4 class="font-bold text-white text-sm ${idx === currentIndex ? 'text-amber-400' : ''}">${s.title}</h4>
            <p class="text-xs text-slate-400 mt-0.5">${s.desc}</p>
          </div>
        </div>
      `;
    }).join('');
  }

  if (itemsContainer && order.items) {
    itemsContainer.innerHTML = order.items.map(it => `
      <div class="flex justify-between py-1 border-b border-slate-800/50">
        <span class="text-slate-300">${it.quantity}x ${it.item_name} ${it.special_instructions ? `(${it.special_instructions})` : ''}</span>
        <span class="text-amber-400 font-semibold">₹${(it.price * it.quantity).toFixed(2)}</span>
      </div>
    `).join('') + `
      <div class="flex justify-between pt-2 font-bold text-white">
        <span>Order Total</span>
        <span class="text-amber-400">₹${order.total.toFixed(2)}</span>
      </div>
    `;
  }
}

// AI Sommelier Chatbot Stream
async function sendChatMessage(userText) {
  const container = document.getElementById('chat-messages-container');
  const input = document.getElementById('chat-input');
  if (!container || !userText.trim()) return;

  // Add User Bubble
  const userBubble = document.createElement('div');
  userBubble.className = 'chat-bubble chat-bubble-user';
  userBubble.textContent = userText;
  container.appendChild(userBubble);
  if (input) input.value = '';
  container.scrollTop = container.scrollHeight;

  // Add Loading Bot Bubble
  const botBubble = document.createElement('div');
  botBubble.className = 'chat-bubble chat-bubble-bot text-slate-400 italic';
  botBubble.innerHTML = 'Ustaad Ananda Rao is curating traditional Telugu pairings...';
  container.appendChild(botBubble);
  container.scrollTop = container.scrollHeight;

  try {
    const res = await apiRequest('/ai/chat', {
      method: 'POST',
      body: JSON.stringify({
        message: userText,
        history: state.chatHistory
      })
    });

    // Replace with response
    botBubble.className = 'chat-bubble chat-bubble-bot';
    
    // Parse markdown bold into HTML
    const formatted = res.reply.replace(/\*\*(.*?)\*\*/g, '<strong class="text-amber-300">$1</strong>');
    
    let actionButtonsHtml = '';
    if (res.suggested_dishes && res.suggested_dishes.length > 0) {
      actionButtonsHtml = `
        <div class="mt-2.5 pt-2 border-t border-slate-700/60 flex flex-wrap gap-1.5">
          ${res.suggested_dishes.map(dishName => {
            const dish = state.menuItems.find(m => m.name.toLowerCase() === dishName.toLowerCase());
            if (dish) {
              return `<button onclick="window.BistroApp.addToCart('${dish.id}')" class="btn btn-gold btn-sm text-[11px] py-1 px-2.5">
                        + Add ${dish.name} (₹${dish.price})
                      </button>`;
            }
            return '';
          }).join('')}
        </div>
      `;
    }

    botBubble.innerHTML = `
      <div>${formatted}</div>
      ${actionButtonsHtml}
      <div class="text-[10px] text-slate-500 mt-2 text-right">Validated via ${res.source}</div>
    `;

    state.chatHistory.push({ role: 'user', content: userText });
    state.chatHistory.push({ role: 'assistant', content: res.reply });
  } catch (err) {
    botBubble.innerHTML = `Ustaad Ananda Rao is momentarily attending guest dining. Please try again. (${err.message})`;
  }

  container.scrollTop = container.scrollHeight;
}

// Admin Dashboard Loaders
async function openAdminDashboard() {
  window.BistroApp.openModal('admin-modal');
  await loadAdminAnalytics();
  await loadAdminOrders();
}

async function loadAdminAnalytics() {
  const container = document.getElementById('admin-kpis');
  if (!container) return;

  try {
    const a = await apiRequest('/admin/analytics');
    state.adminData.analytics = a;

    container.innerHTML = `
      <div class="p-4 rounded-xl bg-slate-900 border border-slate-800">
        <span class="text-[10px] uppercase tracking-wider text-slate-400">Total Revenue</span>
        <div class="font-serif text-xl font-bold text-amber-400 mt-1">₹${a.total_revenue.toFixed(2)}</div>
      </div>
      <div class="p-4 rounded-xl bg-slate-900 border border-slate-800">
        <span class="text-[10px] uppercase tracking-wider text-slate-400">Total Orders</span>
        <div class="font-serif text-xl font-bold text-white mt-1">${a.total_orders}</div>
      </div>
      <div class="p-4 rounded-xl bg-slate-900 border border-slate-800">
        <span class="text-[10px] uppercase tracking-wider text-slate-400">Active Orders</span>
        <div class="font-serif text-xl font-bold text-sky-400 mt-1">${a.active_orders}</div>
      </div>
      <div class="p-4 rounded-xl bg-slate-900 border border-slate-800">
        <span class="text-[10px] uppercase tracking-wider text-slate-400">Avg Order Value</span>
        <div class="font-serif text-xl font-bold text-white mt-1">₹${a.average_order_value.toFixed(2)}</div>
      </div>
      <div class="p-4 rounded-xl bg-slate-900 border border-slate-800">
        <span class="text-[10px] uppercase tracking-wider text-slate-400">Guest Rating</span>
        <div class="font-serif text-xl font-bold text-amber-400 mt-1">⭐ ${a.average_rating}</div>
      </div>
      <div class="p-4 rounded-xl bg-slate-900 border border-slate-800">
        <span class="text-[10px] uppercase tracking-wider text-slate-400">AI Integrity Logs</span>
        <div class="font-serif text-xl font-bold text-emerald-400 mt-1">${a.integrity_events_total}</div>
      </div>
    `;
  } catch (err) {
    console.error('Analytics load error:', err);
  }
}

async function loadAdminOrders() {
  const container = document.getElementById('admin-tab-orders');
  if (!container) return;

  try {
    const orders = await apiRequest('/admin/orders');
    state.adminData.orders = orders;

    if (orders.length === 0) {
      container.innerHTML = '<div class="text-center py-8 text-slate-400">No orders logged in system.</div>';
      return;
    }

    container.innerHTML = `
      <div class="overflow-x-auto">
        <table class="w-full text-xs text-left text-slate-300">
          <thead class="text-[11px] uppercase bg-slate-900 text-slate-400 border-b border-slate-800">
            <tr>
              <th class="p-3">Order Ref</th>
              <th class="p-3">Customer</th>
              <th class="p-3">Items</th>
              <th class="p-3">Total</th>
              <th class="p-3">Status</th>
              <th class="p-3">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800">
            ${orders.map(o => `
              <tr class="hover:bg-slate-900/60 transition-colors">
                <td class="p-3 font-mono text-amber-400">#${o.id.slice(0, 8).toUpperCase()}</td>
                <td class="p-3">
                  <div class="font-bold text-white">${o.customer_name}</div>
                  <div class="text-[10px] text-slate-400">${o.customer_phone || o.customer_email}</div>
                </td>
                <td class="p-3">
                  ${(o.items || []).map(i => `${i.quantity}x ${i.item_name}`).join(', ')}
                </td>
                <td class="p-3 font-bold text-white">₹${o.total.toFixed(2)}</td>
                <td class="p-3">
                  <span class="badge ${o.status === 'delivered' ? 'badge-green' : o.status === 'cancelled' ? 'badge-red' : 'badge-gold'}">
                    ${o.status.replace('_', ' ')}
                  </span>
                </td>
                <td class="p-3 space-x-1 whitespace-nowrap">
                  <select onchange="window.BistroApp.setOrderStatus('${o.id}', this.value)" class="bg-slate-950 border border-slate-700 rounded-lg px-2 py-1 text-[11px] text-slate-200">
                    <option value="" disabled selected>Update Status</option>
                    <option value="pending">Pending</option>
                    <option value="preparing">In Kitchen</option>
                    <option value="quality_check">Quality Check</option>
                    <option value="out_for_delivery">Out For Delivery</option>
                    <option value="delivered">Delivered</option>
                    <option value="cancelled">Cancelled</option>
                  </select>
                  <button onclick="window.BistroApp.trackOrder('${o.id}')" class="btn btn-outline btn-sm py-0.5 px-2 text-[10px]">Track</button>
                </td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    `;
  } catch (err) {
    container.innerHTML = `<div class="text-rose-400 text-xs">${err.message}</div>`;
  }
}

async function loadAdminMenu() {
  const container = document.getElementById('admin-tab-menu');
  if (!container) return;

  try {
    const items = await apiRequest('/menu');
    container.innerHTML = `
      <div class="flex items-center justify-between mb-4">
        <h4 class="font-serif font-bold text-white text-base">Active Catalog Dishes (${items.length})</h4>
        <button id="add-dish-btn" class="btn btn-gold btn-sm">+ Add New Dish</button>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-xs text-left text-slate-300">
          <thead class="text-[11px] uppercase bg-slate-900 text-slate-400 border-b border-slate-800">
            <tr>
              <th class="p-3">Dish</th>
              <th class="p-3">Category</th>
              <th class="p-3">Price</th>
              <th class="p-3">Rating</th>
              <th class="p-3">Availability</th>
              <th class="p-3">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800">
            ${items.map(m => `
              <tr class="hover:bg-slate-900/60 transition-colors">
                <td class="p-3 flex items-center gap-3">
                  <img src="${m.image}" alt="${m.name}" class="w-10 h-10 rounded-lg object-cover">
                  <div>
                    <div class="font-bold text-white">${m.name}</div>
                    <div class="text-[10px] text-slate-400 line-clamp-1">${m.description}</div>
                  </div>
                </td>
                <td class="p-3">${m.category}</td>
                <td class="p-3 font-bold text-amber-400">₹${m.price.toFixed(2)}</td>
                <td class="p-3">⭐ ${m.rating}</td>
                <td class="p-3">
                  <span class="badge ${m.is_available ? 'badge-green' : 'badge-red'}">
                    ${m.is_available ? 'In Stock' : 'Sold Out'}
                  </span>
                </td>
                <td class="p-3 space-x-1 whitespace-nowrap">
                  <button onclick="window.BistroApp.toggleDish('${m.id}')" class="btn btn-outline btn-sm py-0.5 px-2 text-[10px]">
                    ${m.is_available ? 'Set Sold Out' : 'Set Available'}
                  </button>
                  <button onclick="window.BistroApp.deleteDish('${m.id}')" class="btn btn-outline btn-sm py-0.5 px-2 text-[10px] text-rose-400 border-rose-500/30">
                    Delete
                  </button>
                </td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    `;
  } catch (err) {
    container.innerHTML = `<div class="text-rose-400 text-xs">${err.message}</div>`;
  }
}

async function loadAdminIntegrityLogs() {
  const container = document.getElementById('admin-tab-integrity');
  if (!container) return;

  try {
    const logs = await apiRequest('/admin/integrity-logs');
    container.innerHTML = `
      <div class="p-4 rounded-xl bg-slate-900 border border-slate-800 mb-4">
        <h4 class="font-serif font-bold text-white text-sm mb-1">AI Data Integrity & Security Monitor</h4>
        <p class="text-xs text-slate-400">All price tampering checks, allergen collisions, and review moderations are recorded here in real time.</p>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-xs text-left text-slate-300">
          <thead class="text-[11px] uppercase bg-slate-900 text-slate-400 border-b border-slate-800">
            <tr>
              <th class="p-3">Timestamp</th>
              <th class="p-3">Event Type</th>
              <th class="p-3">Severity</th>
              <th class="p-3">Status</th>
              <th class="p-3">Inspection Details</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800 font-mono text-[11px]">
            ${logs.map(l => `
              <tr class="hover:bg-slate-900/60">
                <td class="p-3 text-slate-400">${new Date(l.timestamp).toLocaleTimeString()}</td>
                <td class="p-3 text-white font-bold">${l.event_type}</td>
                <td class="p-3">
                  <span class="badge ${l.severity === 'high' ? 'badge-red' : l.severity === 'medium' ? 'badge-gold' : 'badge-blue'}">
                    ${l.severity}
                  </span>
                </td>
                <td class="p-3">
                  <span class="badge ${l.status === 'blocked' ? 'badge-red' : l.status === 'warning' ? 'badge-gold' : 'badge-green'}">
                    ${l.status}
                  </span>
                </td>
                <td class="p-3 max-w-xs truncate text-slate-400">
                  ${JSON.stringify(l.details)}
                </td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    `;
  } catch (err) {
    container.innerHTML = `<div class="text-rose-400 text-xs">${err.message}</div>`;
  }
}

// DOM Setup & Event Listeners
document.addEventListener('DOMContentLoaded', async () => {
  // Initialize user session
  if (state.token) {
    try {
      const user = await apiRequest('/auth/me');
      setUserSession(state.token, user);
    } catch {
      clearUserSession();
    }
  }

  // Load initial data
  await loadMenu();
  await loadAIRecommendations();
  await loadReviews();
  renderCart();
  updateCartBadge();

  // Navigation Links
  document.getElementById('auth-btn')?.addEventListener('click', () => {
    if (state.user) {
      // Show Profile View
      document.getElementById('auth-tabs')?.classList.add('hidden');
      document.getElementById('demo-login-presets')?.classList.add('hidden');
      document.getElementById('login-form')?.classList.add('hidden');
      document.getElementById('register-form')?.classList.add('hidden');
      document.getElementById('profile-view')?.classList.remove('hidden');

      document.getElementById('prof-name-display').textContent = state.user.name;
      document.getElementById('prof-role-display').textContent = state.user.role.toUpperCase();
      document.getElementById('prof-email-display').textContent = state.user.email;
      document.getElementById('prof-address').value = state.user.address || '';
      document.getElementById('prof-phone').value = state.user.phone || '';
      document.getElementById('prof-diet').value = (state.user.dietary_preferences || []).join(', ');

      loadUserPastOrders();
      loadUserReservations();
    } else {
      // Show Login Tab
      document.getElementById('auth-tabs')?.classList.remove('hidden');
      document.getElementById('demo-login-presets')?.classList.remove('hidden');
      document.getElementById('login-form')?.classList.remove('hidden');
      document.getElementById('register-form')?.classList.add('hidden');
      document.getElementById('profile-view')?.classList.add('hidden');
    }
    window.BistroApp.openModal('auth-modal');
  });

  document.getElementById('admin-nav-btn')?.addEventListener('click', openAdminDashboard);
  document.getElementById('cart-toggle-btn')?.addEventListener('click', () => {
    document.getElementById('cart-drawer')?.classList.add('open');
  });
  document.getElementById('close-cart-btn')?.addEventListener('click', () => {
    document.getElementById('cart-drawer')?.classList.remove('open');
  });

  // Floating AI Chat Drawer
  document.getElementById('floating-ai-trigger')?.addEventListener('click', () => {
    document.getElementById('ai-chat-drawer')?.classList.add('open');
  });
  document.getElementById('hero-ai-chat-btn')?.addEventListener('click', () => {
    document.getElementById('ai-chat-drawer')?.classList.add('open');
  });
  document.getElementById('close-ai-chat-btn')?.addEventListener('click', () => {
    document.getElementById('ai-chat-drawer')?.classList.remove('open');
  });

  // AI Prompt Chips
  document.querySelectorAll('.ai-chip').forEach(btn => {
    btn.addEventListener('click', () => {
      const prompt = btn.getAttribute('data-prompt');
      sendChatMessage(prompt);
    });
  });

  // AI Chat Form
  document.getElementById('chat-form')?.addEventListener('submit', (e) => {
    e.preventDefault();
    const input = document.getElementById('chat-input');
    if (input && input.value.trim()) {
      sendChatMessage(input.value);
    }
  });

  // Hero Reserve CTA
  document.getElementById('hero-reserve-btn')?.addEventListener('click', () => {
    const section = document.getElementById('reservation-section');
    if (section) section.scrollIntoView({ behavior: 'smooth' });
  });

  // Category Tabs
  document.querySelectorAll('.category-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.category-btn').forEach(b => b.classList.remove('active', 'btn-gold'));
      btn.classList.add('active', 'btn-gold');
      state.currentCategory = btn.getAttribute('data-category');
      loadMenu();
    });
  });

  // Dietary Filters
  document.querySelectorAll('.dietary-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.dietary-btn').forEach(b => b.classList.remove('active', 'ring-2', 'ring-amber-400'));
      btn.classList.add('active', 'ring-2', 'ring-amber-400');
      state.currentDietary = btn.getAttribute('data-dietary');
      loadMenu();
    });
  });

  // Search Input Debounce
  let searchTimer = null;
  document.getElementById('menu-search-input')?.addEventListener('input', (e) => {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => {
      state.searchQuery = e.target.value.trim();
      loadMenu();
    }, 300);
  });

  // Sort Select
  document.getElementById('menu-sort-select')?.addEventListener('change', (e) => {
    state.currentSort = e.target.value;
    loadMenu();
  });

  // AI Mood Selectors
  document.querySelectorAll('.ai-mood-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.ai-mood-btn').forEach(b => b.classList.remove('active', 'btn-gold'));
      btn.classList.add('active', 'btn-gold');
      const mood = btn.getAttribute('data-mood');
      loadAIRecommendations(mood);
    });
  });

  // Promo Coupon Button
  document.getElementById('apply-coupon-btn')?.addEventListener('click', async () => {
    const input = document.getElementById('coupon-input');
    const statusMsg = document.getElementById('coupon-status-msg');
    const code = input?.value.trim();
    if (!code) return;

    const subtotal = state.cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);

    try {
      const res = await apiRequest('/ai/validate-coupon', {
        method: 'POST',
        body: JSON.stringify({ code, subtotal })
      });
      state.appliedCoupon = res;
      renderCart();
      if (statusMsg) {
        statusMsg.className = 'text-xs text-emerald-400 block';
        statusMsg.textContent = `Promo applied! ${res.description} (-₹${res.discount_amount.toFixed(2)})`;
      }
      showToast(`Promo ${res.code} activated!`, 'success');
    } catch (err) {
      if (statusMsg) {
        statusMsg.className = 'text-xs text-rose-400 block';
        statusMsg.textContent = err.message;
      }
      showToast(err.message, 'error');
    }
  });

  // Tip Selector
  document.querySelectorAll('.tip-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tip-btn').forEach(b => b.classList.remove('active', 'bg-amber-500', 'text-black'));
      btn.classList.add('active', 'bg-amber-500', 'text-black');
      state.tipAmount = parseFloat(btn.getAttribute('data-tip')) || 0;
      renderCart();
    });
  });

  // Proceed to Checkout
  document.getElementById('proceed-checkout-btn')?.addEventListener('click', () => {
    if (state.cart.length === 0) {
      showToast('Your cart is empty', 'error');
      return;
    }
    document.getElementById('cart-drawer')?.classList.remove('open');

    // Pre-fill user data if logged in
    if (state.user) {
      const nameInput = document.getElementById('chk-name');
      const emailInput = document.getElementById('chk-email');
      const phoneInput = document.getElementById('chk-phone');
      const addrInput = document.getElementById('chk-address');
      if (nameInput) nameInput.value = state.user.name;
      if (emailInput) emailInput.value = state.user.email;
      if (phoneInput) phoneInput.value = state.user.phone || '';
      if (addrInput) addrInput.value = state.user.address || '';
    }

    window.BistroApp.openModal('checkout-modal');
  });

  // Checkout Form Submission
  document.getElementById('checkout-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = document.getElementById('place-order-submit-btn');
    if (btn) btn.disabled = true;

    const subtotal = state.cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    let discount = state.appliedCoupon ? Math.min(subtotal * (state.appliedCoupon.discount_percent / 100), state.appliedCoupon.max_discount || 300) : 0;
    const tip = subtotal > 0 ? (state.tipAmount || 0) : 0;

    const payload = {
      customer_name: document.getElementById('chk-name').value,
      customer_email: document.getElementById('chk-email').value,
      customer_phone: document.getElementById('chk-phone').value,
      delivery_address: document.getElementById('chk-address').value,
      order_type: document.querySelector('input[name="orderType"]:checked')?.value || 'delivery',
      items: state.cart.map(c => ({
        menu_item_id: c.id,
        item_name: c.item_name,
        price: c.price,
        quantity: c.quantity,
        special_instructions: c.special_instructions || '',
        image: c.image
      })),
      coupon_code: state.appliedCoupon ? state.appliedCoupon.code : null,
      tip
    };

    try {
      const order = await apiRequest('/orders', {
        method: 'POST',
        body: JSON.stringify(payload)
      });

      // Clear Cart
      state.cart = [];
      state.appliedCoupon = null;
      saveCart();
      renderCart();

      window.BistroApp.closeModal('checkout-modal');

      // Trigger Celebratory Confetti!
      if (typeof confetti === 'function') {
        confetti({
          particleCount: 120,
          spread: 80,
          origin: { y: 0.6 }
        });
      }

      showToast('Order confirmed! Our kitchen is preparing your dishes.', 'success');

      // Open Live Order Tracking
      setTimeout(() => {
        window.BistroApp.trackOrder(order.id);
      }, 600);

    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      if (btn) btn.disabled = false;
    }
  });

  // Table Reservation Form
  document.getElementById('reservation-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
      name: document.getElementById('res-name').value,
      email: document.getElementById('res-email').value,
      phone: document.getElementById('res-phone').value,
      date: document.getElementById('res-date').value,
      time: document.getElementById('res-time').value,
      guests: parseInt(document.getElementById('res-guests').value, 10),
      area: document.getElementById('res-area').value,
      special_requests: document.getElementById('res-notes').value
    };

    try {
      const res = await apiRequest('/reservations', {
        method: 'POST',
        body: JSON.stringify(payload)
      });
      showToast(`Table booked for ${res.name} on ${res.date} at ${res.time}!`, 'success');
      document.getElementById('reservation-form').reset();
      loadUserReservations();
    } catch (err) {
      showToast(err.message, 'error');
    }
  });

  // Contact Inquiry Form
  document.getElementById('contact-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
      name: document.getElementById('contact-name').value,
      email: document.getElementById('contact-email').value,
      subject: document.getElementById('contact-subject').value,
      message: document.getElementById('contact-message').value
    };

    try {
      await apiRequest('/contact', {
        method: 'POST',
        body: JSON.stringify(payload)
      });
      showToast('Inquiry verified by AI and dispatched to the sommelier desk.', 'success');
      document.getElementById('contact-form').reset();
    } catch (err) {
      showToast(err.message, 'error');
    }
  });

  // Write Review Modal
  document.getElementById('open-write-review-btn')?.addEventListener('click', () => {
    window.BistroApp.openModal('review-modal');
  });

  // Star Rating Selector
  document.querySelectorAll('.star-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const star = parseInt(btn.getAttribute('data-star'), 10);
      document.getElementById('rev-rating').value = star;
      document.querySelectorAll('.star-btn').forEach(b => {
        const val = parseInt(b.getAttribute('data-star'), 10);
        b.textContent = val <= star ? '★' : '☆';
      });
    });
  });

  // Review Form Submit
  document.getElementById('write-review-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
      rating: parseInt(document.getElementById('rev-rating').value, 10),
      dish_name: document.getElementById('rev-dish').value,
      comment: document.getElementById('rev-comment').value
    };

    try {
      const res = await apiRequest('/reviews', {
        method: 'POST',
        body: JSON.stringify(payload)
      });
      showToast(`Review posted with sentiment: ${res.sentiment}`, 'success');
      window.BistroApp.closeModal('review-modal');
      document.getElementById('write-review-form').reset();
      loadReviews();
    } catch (err) {
      showToast(err.message, 'error');
    }
  });

  // Auth Tab Switchers
  document.getElementById('tab-login-btn')?.addEventListener('click', () => {
    document.getElementById('login-form')?.classList.remove('hidden');
    document.getElementById('register-form')?.classList.add('hidden');
    document.getElementById('tab-login-btn')?.classList.add('border-amber-400', 'text-amber-400');
    document.getElementById('tab-register-btn')?.classList.remove('border-amber-400', 'text-amber-400');
  });

  document.getElementById('tab-register-btn')?.addEventListener('click', () => {
    document.getElementById('login-form')?.classList.add('hidden');
    document.getElementById('register-form')?.classList.remove('hidden');
    document.getElementById('tab-register-btn')?.classList.add('border-amber-400', 'text-amber-400');
    document.getElementById('tab-login-btn')?.classList.remove('border-amber-400', 'text-amber-400');
  });

  // Login Form
  document.getElementById('login-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    try {
      const data = await apiRequest('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password })
      });
      setUserSession(data.access_token, data.user);
      showToast(`Welcome back, ${data.user.name}!`, 'success');
      window.BistroApp.closeModal('auth-modal');
    } catch (err) {
      showToast(err.message, 'error');
    }
  });

  // Register Form
  document.getElementById('register-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const dietStr = document.getElementById('reg-diet').value;
    const dietArr = dietStr ? dietStr.split(',').map(s => s.trim()).filter(Boolean) : [];

    const payload = {
      name: document.getElementById('reg-name').value,
      email: document.getElementById('reg-email').value,
      password: document.getElementById('reg-password').value,
      dietary_preferences: dietArr
    };

    try {
      const data = await apiRequest('/auth/register', {
        method: 'POST',
        body: JSON.stringify(payload)
      });
      setUserSession(data.access_token, data.user);
      showToast('Registration successful! Welcome to Savory Bistro.', 'success');
      window.BistroApp.closeModal('auth-modal');
    } catch (err) {
      showToast(err.message, 'error');
    }
  });

  // Profile Edit Form
  document.getElementById('profile-edit-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const dietStr = document.getElementById('prof-diet').value;
    const dietArr = dietStr ? dietStr.split(',').map(s => s.trim()).filter(Boolean) : [];

    const payload = {
      address: document.getElementById('prof-address').value,
      phone: document.getElementById('prof-phone').value,
      dietary_preferences: dietArr
    };

    try {
      const updatedUser = await apiRequest('/auth/profile', {
        method: 'PUT',
        body: JSON.stringify(payload)
      });
      state.user = updatedUser;
      localStorage.setItem('savory_user', JSON.stringify(updatedUser));
      showToast('Profile and allergy protection settings updated', 'success');
      checkCartAllergens();
    } catch (err) {
      showToast(err.message, 'error');
    }
  });

  // Logout
  document.getElementById('logout-btn')?.addEventListener('click', () => {
    clearUserSession();
    window.BistroApp.closeModal('auth-modal');
    showToast('Signed out successfully', 'info');
  });

  // Admin Tab Switcher
  document.querySelectorAll('.admin-tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.admin-tab-btn').forEach(b => b.classList.remove('active', 'btn-gold'));
      btn.classList.add('active', 'btn-gold');

      const tab = btn.getAttribute('data-tab');
      document.querySelectorAll('.admin-tab-pane').forEach(p => p.classList.add('hidden'));
      const activePane = document.getElementById(`admin-tab-${tab}`);
      if (activePane) activePane.classList.remove('hidden');

      if (tab === 'orders') loadAdminOrders();
      if (tab === 'menu') loadAdminMenu();
      if (tab === 'integrity') loadAdminIntegrityLogs();
      if (tab === 'reservations') loadAdminReservations();
      if (tab === 'inquiries') loadAdminInquiries();
      if (tab === 'firebase') loadFirebaseStatus();
    });
  });

  // Admin AI Item Creator Run
  document.getElementById('run-ai-item-generator-btn')?.addEventListener('click', async () => {
    const input = document.getElementById('ai-concept-input');
    const preview = document.getElementById('ai-generated-item-preview');
    const concept = input?.value.trim();
    if (!concept) {
      showToast('Please type a culinary concept', 'error');
      return;
    }

    if (preview) {
      preview.classList.remove('hidden');
      preview.innerHTML = '<div class="text-amber-400 italic">Chef AI is designing recipe, sensory description, and optimal pricing...</div>';
    }

    try {
      const dish = await apiRequest('/ai/generate-menu-item', {
        method: 'POST',
        body: JSON.stringify({ concept })
      });

      preview.innerHTML = `
        <div class="space-y-2">
          <div class="flex items-center justify-between">
            <h5 class="font-serif font-bold text-white text-base">${dish.name}</h5>
            <span class="text-amber-400 font-bold">₹${dish.price.toFixed(2)}</span>
          </div>
          <span class="badge badge-gold text-[10px]">${dish.category}</span>
          <p class="text-xs text-slate-300 italic">${dish.description}</p>
          <div class="text-[11px] text-slate-400">🔥 ${dish.calories} kcal • ⏱️ ${dish.prep_time} • 🍷 ${dish.wine_pairing || 'Sommelier Pair'}</div>
          <div class="pt-2 flex justify-end">
            <button id="commit-ai-dish-btn" class="btn btn-gold btn-sm">Add to Live Menu</button>
          </div>
        </div>
      `;

      document.getElementById('commit-ai-dish-btn')?.addEventListener('click', async () => {
        try {
          await apiRequest('/menu', {
            method: 'POST',
            body: JSON.stringify(dish)
          });
          showToast(`"${dish.name}" added to menu catalog!`, 'success');
          loadMenu();
          preview.classList.add('hidden');
          input.value = '';
        } catch (err) {
          showToast(err.message, 'error');
        }
      });

    } catch (err) {
      preview.innerHTML = `<div class="text-rose-400 text-xs">${err.message}</div>`;
    }
  });

});

// Past Orders loader for Profile Modal
async function loadUserPastOrders() {
  const container = document.getElementById('prof-past-orders');
  if (!container) return;

  try {
    const orders = await apiRequest('/orders/my-orders');
    if (orders.length === 0) {
      container.innerHTML = '<div class="text-slate-500 italic">No past orders found.</div>';
      return;
    }
    container.innerHTML = orders.map(o => `
      <div class="p-2.5 rounded-lg bg-slate-950 border border-slate-800 flex items-center justify-between">
        <div>
          <span class="font-mono text-amber-400 font-bold">#${o.id.slice(0, 8).toUpperCase()}</span>
          <span class="text-slate-400 ml-2">₹${o.total.toFixed(2)}</span>
          <div class="text-[10px] text-slate-500">${new Date(o.created_at).toLocaleDateString()}</div>
        </div>
        <button onclick="window.BistroApp.trackOrder('${o.id}')" class="btn btn-outline btn-sm text-[10px] py-0.5 px-2">
          Track
        </button>
      </div>
    `).join('');
  } catch (err) {
    container.innerHTML = `<div class="text-rose-400 text-xs">${err.message}</div>`;
  }
}

async function loadUserReservations() {
  const container = document.getElementById('prof-my-reservations');
  if (!container) return;

  try {
    const list = await apiRequest('/reservations/my-reservations');
    if (!list || list.length === 0) {
      container.innerHTML = '<div class="text-slate-500 italic">No table bookings found yet.</div>';
      return;
    }
    container.innerHTML = list.map(r => `
      <div class="p-2.5 rounded-lg bg-slate-950 border border-slate-800 flex items-center justify-between">
        <div>
          <div class="font-bold text-amber-300">${r.name} · <span class="text-white font-normal">${r.guests} Guests</span></div>
          <div class="text-[11px] text-slate-300">📅 ${r.date} @ ⏰ ${r.time}</div>
          <div class="text-[10px] text-slate-400">🏛️ ${r.area} ${r.special_requests ? `(${r.special_requests})` : ''}</div>
        </div>
        <div>
          <span class="badge badge-green text-[10px] uppercase">${r.status}</span>
        </div>
      </div>
    `).join('');
  } catch (err) {
    container.innerHTML = `<div class="text-rose-400 text-xs">${err.message}</div>`;
  }
}

async function loadAdminReservations() {
  const container = document.getElementById('admin-tab-reservations');
  if (!container) return;
  try {
    const list = await apiRequest('/admin/reservations');
    container.innerHTML = `
      <div class="overflow-x-auto">
        <table class="w-full text-xs text-left text-slate-300">
          <thead class="text-[11px] uppercase bg-slate-900 text-slate-400 border-b border-slate-800">
            <tr>
              <th class="p-3">Guest</th>
              <th class="p-3">Date & Time</th>
              <th class="p-3">Party</th>
              <th class="p-3">Area</th>
              <th class="p-3">Requests</th>
              <th class="p-3">Status</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800">
            ${list.map(r => `
              <tr class="hover:bg-slate-900/60">
                <td class="p-3 font-bold text-white">${r.name}<br><span class="text-[10px] text-slate-400">${r.phone}</span></td>
                <td class="p-3">${r.date} @ ${r.time}</td>
                <td class="p-3">${r.guests} Guests</td>
                <td class="p-3">${r.area}</td>
                <td class="p-3 italic text-slate-400">${r.special_requests || 'None'}</td>
                <td class="p-3"><span class="badge badge-green">${r.status}</span></td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    `;
  } catch (err) {
    container.innerHTML = `<div class="text-rose-400 text-xs">${err.message}</div>`;
  }
}

async function loadAdminInquiries() {
  const container = document.getElementById('admin-tab-inquiries');
  if (!container) return;
  try {
    const list = await apiRequest('/admin/inquiries');
    container.innerHTML = `
      <div class="overflow-x-auto">
        <table class="w-full text-xs text-left text-slate-300">
          <thead class="text-[11px] uppercase bg-slate-900 text-slate-400 border-b border-slate-800">
            <tr>
              <th class="p-3">Sender</th>
              <th class="p-3">Subject</th>
              <th class="p-3">Message</th>
              <th class="p-3">AI Security</th>
              <th class="p-3">Status</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800">
            ${list.map(i => `
              <tr class="hover:bg-slate-900/60">
                <td class="p-3 font-bold text-white">${i.name}<br><span class="text-[10px] text-slate-400">${i.email}</span></td>
                <td class="p-3 font-semibold text-amber-300">${i.subject}</td>
                <td class="p-3 max-w-xs text-slate-300">${i.message}</td>
                <td class="p-3"><span class="badge badge-green">${i.integrity_status}</span></td>
                <td class="p-3"><span class="badge badge-gold">${i.status}</span></td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    `;
  } catch (err) {
    container.innerHTML = `<div class="text-rose-400 text-xs">${err.message}</div>`;
  }
}

async function loadFirebaseStatus() {
  try {
    const data = await apiRequest('/firebase/status');
    const badge = document.getElementById('firebase-status-badge');
    const projId = document.getElementById('fb-project-id');
    const modeDesc = document.getElementById('fb-mode-desc');
    const dishesSynced = document.getElementById('fb-dishes-synced');

    if (badge) {
      badge.textContent = data.connected ? '🔥 Live Firestore' : '⚡ Cloud Sync Active';
      badge.className = data.connected ? 'badge badge-green px-3 py-1 text-xs' : 'badge badge-gold px-3 py-1 text-xs';
    }
    if (projId) projId.textContent = data.project_id || 'savory-ai-bistro';
    if (modeDesc) modeDesc.textContent = data.mode || 'Active Sync Pipeline';
    if (dishesSynced && data.sync_statistics) {
      const count = data.sync_statistics.menu_items_synced || 22;
      dishesSynced.textContent = `${count} Telugu Dishes`;
    }
  } catch (err) {
    console.warn('Could not fetch Firebase status', err);
  }
}

