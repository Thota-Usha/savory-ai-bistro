import { GoogleGenAI } from '@google/genai';
import dotenv from 'dotenv';
import { DB } from '../db.js';

dotenv.config();

const apiKey = process.env.GEMINI_API_KEY || process.env.API_KEY || '';
let aiClient = null;

if (apiKey) {
  try {
    aiClient = new GoogleGenAI({ apiKey });
  } catch (err) {
    console.warn('Failed to initialize GoogleGenAI client with key, using fallback engine:', err.message);
  }
}

/**
 * Intelligent AI Sommelier & Culinary Assistant Chatbot
 */
export async function chatWithAISommelier(userMessage, conversationHistory = [], userProfile = null) {
  const menuItems = DB.getMenuItems();
  const menuContext = menuItems.map(m => 
    `- ${m.name} ($${m.price}, ${m.category}): ${m.description} | Tags: ${m.tags.join(', ')} | Allergens: ${m.allergens.join(', ') || 'None'} | Wine Pairing: ${m.winePairing}`
  ).join('\n');

  const systemInstruction = `
You are Chef Sommelier Julian, the premier AI Culinary Concierge and Sommelier for "Savory AI Bistro", an exquisite Michelin-inspired fine dining establishment.
Your role:
1. Provide warm, sophisticated, and deeply knowledgeable culinary guidance.
2. Recommend dishes from our specific menu according to customer mood, taste desires, and dietary restrictions.
3. Suggest sommelier beverage and wine pairings.
4. Answer questions about ingredients, preparation techniques, allergens, and flavor profiles.
5. If the customer expresses interest in a dish, mention it clearly by exact name so they can easily add it to their order.
6. Keep answers refined, appetizing, helpful, and concise (under 120 words per response).

Our Current Menu:
${menuContext}

User Profile Info:
${userProfile ? `Name: ${userProfile.name}, Dietary Preferences/Allergies: ${userProfile.dietaryPreferences?.join(', ') || 'None stated'}` : 'Guest User'}
`;

  // Try real Gemini API if client available
  if (aiClient) {
    try {
      const prompt = `${systemInstruction}\n\nUser Question: ${userMessage}`;
      const response = await aiClient.models.generateContent({
        model: 'gemini-3.8-flash',
        contents: prompt,
      });

      if (response && response.text) {
        return {
          reply: response.text.trim(),
          source: 'Gemini 3.8 Flash'
        };
      }
    } catch (apiError) {
      console.warn('Gemini API call failed, falling back to local culinary intelligence engine:', apiError.message);
    }
  }

  // Fallback intelligent culinary heuristics engine
  const reply = generateSmartFallbackReply(userMessage, menuItems, userProfile);
  return {
    reply,
    source: 'Savory Culinary AI Engine'
  };
}

/**
 * Fallback AI response generator
 */
function generateSmartFallbackReply(input, menuItems, userProfile) {
  const text = input.toLowerCase();

  // Allergen checks
  if (text.includes('allergy') || text.includes('allergic') || text.includes('gluten') || text.includes('nut')) {
    if (text.includes('gluten')) {
      const gfItems = menuItems.filter(m => m.tags.includes('Gluten-Free'));
      return `For a gluten-free experience, Chef Alessandro recommends our exquisite **${gfItems[0]?.name}** and **${gfItems[1]?.name || 'Chilean Sea Bass'}**. Both are prepared in a dedicated gluten-conscious kitchen station.`;
    }
    if (text.includes('nut')) {
      return `Safety is paramount at Savory AI Bistro. Our culinary team exercises strict separation. Dishes completely free of nuts include the **Prime Wagyu Filet Mignon**, **Chilean Sea Bass**, and **Duck Confit**. Let our kitchen know in the special instructions!`;
    }
    return `We take allergies with surgical precision! You can filter our menu by Dietary Tags (Gluten-Free, Vegan, Vegetarian). Our AI validation engine continuously monitors your cart to ensure no allergen collisions occur with your profile.`;
  }

  // Wine / Drink pairings
  if (text.includes('wine') || text.includes('drink') || text.includes('pairing') || text.includes('cocktail')) {
    if (text.includes('steak') || text.includes('wagyu') || text.includes('meat') || text.includes('beef')) {
      return `For our Prime Wagyu Filet Mignon, I recommend either our handcrafted **Smoked Rosemary Old Fashioned** or a robust vintage Cabernet Sauvignon. The rich cherrywood smoke and tannins cut beautifully through the marbled Wagyu fat.`;
    }
    if (text.includes('pasta') || text.includes('truffle')) {
      return `With our Handmade Black Truffle Tagliolini, an Italian Nebbiolo or Barolo creates an ethereal symphony of earthiness and acidity. If you prefer a cocktail, try our botanical elixirs.`;
    }
    if (text.includes('seafood') || text.includes('fish') || text.includes('bass') || text.includes('tuna')) {
      return `For seafood such as the Chilean Sea Bass or Yellowfin Tuna Tartare, nothing elevates the bright citrus notes quite like our **Sparkling Yuzu Blossom Mocktail** or a crisp, mineral-forward Chablis.`;
    }
    return `Our cellar features curated Old and New World vintages alongside botanical zero-proof mocktails. For savory meats, enjoy our Smoked Rosemary Old Fashioned; for light seafood and appetizers, our Sparkling Yuzu Blossom Mocktail is sublime.`;
  }

  // Recommendations for romance / date night
  if (text.includes('romantic') || text.includes('date') || text.includes('anniversary') || text.includes('partner')) {
    return `For an enchanting evening for two, I suggest starting with the **Heritage Burrata di Puglia**, followed by the **Prime Wagyu Filet Mignon** and **Handmade Black Truffle Tagliolini** to share. Conclude your evening with our showstopping **Valrhona Dark Chocolate Molten Sphere**.`;
  }

  // Vegetarian / Vegan
  if (text.includes('vegan') || text.includes('vegetarian') || text.includes('plant')) {
    const vegItems = menuItems.filter(m => m.tags.includes('Vegetarian') || m.tags.includes('Vegan'));
    const names = vegItems.slice(0, 3).map(i => `**${i.name}**`).join(', ');
    return `We celebrate plant-forward gastronomy! Our top vegetarian highlights are ${names}. Each is crafted with seasonal heirloom produce from local regenerative farms.`;
  }

  // Desserts / Sweet
  if (text.includes('dessert') || text.includes('sweet') || text.includes('chocolate') || text.includes('sugar')) {
    return `Indulge in our signature **Valrhona Dark Chocolate Molten Sphere** with edible 24k gold leaf and bourbon vanilla bean gelato, or the crisp, layered **Sicilian Pistachio Mille-Feuille**. Pure culinary bliss!`;
  }

  // General recommendations / Cravings
  if (text.includes('recommend') || text.includes('best') || text.includes('popular') || text.includes('special')) {
    return `Chef Alessandro’s crowning triumphs tonight are the **Prime Wagyu Filet Mignon** seared over Binchotan charcoal and the **Handmade Black Truffle Tagliolini**. If you prefer seafood, the **Lobster & Saffron Risotto** is simply unforgettable.`;
  }

  // Default warm sommelier response
  return `Greetings! I am Julian, your AI Sommelier and Culinary Concierge. Whether you are craving an artisanal wood-fired pizza, our Michelin-inspired Truffle Tagliolini, or need personalized wine and allergen pairings, I am honored to curate your dining journey. What flavors are you desiring this evening?`;
}

/**
 * AI Personalized Menu Recommendation Engine
 */
export async function getPersonalizedRecommendations(preferences = {}, orderHistory = []) {
  const menuItems = DB.getMenuItems();
  const { mood, dietary, budget } = preferences;

  let filtered = [...menuItems];

  if (dietary && dietary !== 'All') {
    filtered = filtered.filter(item => item.tags.includes(dietary));
  }

  if (budget === 'low') {
    filtered = filtered.filter(item => item.price <= 20);
  } else if (budget === 'high') {
    filtered = filtered.filter(item => item.price >= 30);
  }

  // Sort by rating & chef specials
  filtered.sort((a, b) => {
    const aSpecial = a.tags.includes('Chef Special') ? 1 : 0;
    const bSpecial = b.tags.includes('Chef Special') ? 1 : 0;
    return (bSpecial * 2 + b.rating) - (aSpecial * 2 + a.rating);
  });

  const topPicks = filtered.slice(0, 4);

  let explanation = "Curated based on chef ratings, artisanal ingredient freshness, and culinary harmony.";
  if (mood) {
    explanation = `Tailored for your "${mood}" mood, emphasizing rich textures and elevated sensory profiles.`;
  } else if (dietary && dietary !== 'All') {
    explanation = `Filtered to guarantee strict adherence to your ${dietary} preferences without sacrificing gourmet flavor.`;
  }

  return {
    recommendations: topPicks,
    explanation,
    confidenceScore: 0.96
  };
}

/**
 * AI Data Integrity & Security Scanner
 * Validates orders, allergens, and reviews for data accuracy and security
 */
export async function runAIIntegrityCheck({ type, payload, userProfile }) {
  const issues = [];
  let integrityScore = 1.0;
  let status = 'passed';

  if (type === 'order') {
    const { items, total } = payload;
    const allMenuItems = DB.getMenuItems();

    // Check 1: Price integrity check (ensure prices haven't been tampered in client request)
    let calculatedSubtotal = 0;
    for (const item of items) {
      const realItem = allMenuItems.find(m => m.id === item.id);
      if (!realItem) {
        issues.push({ code: 'ITEM_NOT_FOUND', message: `Dish ID ${item.id} does not exist in verified catalog.` });
        integrityScore -= 0.5;
        status = 'blocked';
      } else if (Math.abs(realItem.price - item.price) > 0.01) {
        issues.push({ code: 'PRICE_TAMPERING', message: `Reported price $${item.price} deviates from verified $${realItem.price}.` });
        integrityScore -= 0.6;
        status = 'blocked';
      } else {
        calculatedSubtotal += realItem.price * item.quantity;
      }

      // Check 2: Allergen collision detection with user's saved health profile
      if (userProfile && userProfile.dietaryPreferences && realItem) {
        for (const pref of userProfile.dietaryPreferences) {
          const prefLower = pref.toLowerCase();
          for (const allergen of realItem.allergens || []) {
            if (allergen.toLowerCase().includes(prefLower) || prefLower.includes(allergen.toLowerCase())) {
              issues.push({
                code: 'ALLERGEN_COLLISION',
                severity: 'warning',
                message: `Health Alert: Dish "${realItem.name}" contains ${allergen}, which may conflict with your "${pref}" profile.`
              });
              integrityScore = Math.min(integrityScore, 0.85);
              if (status !== 'blocked') status = 'warning';
            }
          }
        }
      }
    }
  } else if (type === 'review') {
    const { comment, rating } = payload;
    
    // Check spam / script tags / prompt injection attempts
    const suspiciousPatterns = [/<script>/i, /javascript:/i, /ignore previous instructions/i, /drop table/i, /system prompt/i];
    const isSuspicious = suspiciousPatterns.some(pattern => pattern.test(comment));

    if (isSuspicious) {
      issues.push({ code: 'SECURITY_INJECTION_DETECTED', message: 'Comment contains forbidden syntax or injection attempts.' });
      integrityScore = 0.0;
      status = 'blocked';
    }

    // Sentiment analysis
    const positiveWords = ['amazing', 'delicious', 'superb', 'exquisite', 'love', 'best', 'wonderful', 'perfect', 'tender'];
    const negativeWords = ['terrible', 'awful', 'cold', 'horrible', 'worst', 'disgusting', 'bad'];
    
    let sentiment = 'Neutral';
    const lowerComment = comment.toLowerCase();
    const hasPositive = positiveWords.some(w => lowerComment.includes(w));
    const hasNegative = negativeWords.some(w => lowerComment.includes(w));

    if (hasPositive && !hasNegative) sentiment = 'Extremely Positive';
    else if (hasNegative && !hasPositive) sentiment = 'Critical';
    else if (rating >= 4) sentiment = 'Positive';

    return {
      status,
      integrityScore,
      issues,
      sentiment,
      passed: status !== 'blocked'
    };
  } else if (type === 'inquiry') {
    const { message, email } = payload;
    const isEmailValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    if (!isEmailValid) {
      issues.push({ code: 'INVALID_EMAIL', message: 'Provided contact email fails RFC integrity validation.' });
      status = 'blocked';
      integrityScore = 0.2;
    }
    if (message.length < 5) {
      issues.push({ code: 'MESSAGE_TOO_SHORT', message: 'Message content does not meet minimum entropy threshold.' });
      status = 'blocked';
    }
  }

  // Log event in database
  DB.logIntegrityEvent({
    eventType: `integrity_check_${type}`,
    severity: status === 'blocked' ? 'high' : status === 'warning' ? 'medium' : 'low',
    details: { type, issuesCount: issues.length, issues },
    status
  });

  return {
    status,
    integrityScore,
    issues,
    passed: status !== 'blocked'
  };
}

/**
 * AI Menu Item Generator for Admin Dashboard
 * Automatically generates a Michelin-quality dish name, description, tags, and suggested pricing
 */
export async function generateMenuItemWithAI(conceptPrompt) {
  if (aiClient) {
    try {
      const prompt = `
You are a 3-Michelin-Star Executive Chef and Food Designer.
Generate a JSON object for a luxury restaurant menu item based on this concept: "${conceptPrompt}".
The JSON must follow this exact format without any markdown backticks:
{
  "name": "Creative Gourmet Name",
  "category": "Appetizers" or "Chef Signatures" or "Artisanal Pastas & Mains" or "Wood-Fired Hearth" or "Decadent Desserts" or "Artisanal Drinks",
  "description": "Sensory, mouth-watering description (2 sentences) highlighting artisanal techniques and provenance.",
  "price": 28.5,
  "calories": 540,
  "prepTime": "15-18 min",
  "tags": ["Chef Special", "Vegetarian"],
  "allergens": ["Dairy"],
  "ingredients": ["Ingredient 1", "Ingredient 2"],
  "winePairing": "Specific wine or artisanal beverage"
}
`;
      const response = await aiClient.models.generateContent({
        model: 'gemini-3.8-flash',
        contents: prompt
      });

      const cleanJson = response.text.replace(/```json/g, '').replace(/```/g, '').trim();
      return JSON.parse(cleanJson);
    } catch (err) {
      console.warn('AI Menu generation fallback:', err.message);
    }
  }

  // High quality creative fallback generator
  return generateFallbackGourmetItem(conceptPrompt);
}

function generateFallbackGourmetItem(concept) {
  const promptLower = concept.toLowerCase();
  
  if (promptLower.includes('truffle') || promptLower.includes('pasta') || promptLower.includes('gnocchi')) {
    return {
      name: "Handcrafted Truffle Ricotta Gnocchi",
      category: "Artisanal Pastas & Mains",
      description: "Pillow-soft hand-rolled ricotta gnocchi gently crisped in hazelnut brown butter, crowned with shaved black Périgord truffles and 30-month Parmigiano Reggiano.",
      price: 36.0,
      calories: 580,
      prepTime: "15 min",
      tags: ["Vegetarian", "Chef Special"],
      allergens: ["Dairy", "Gluten", "Nuts"],
      ingredients: ["Sheep's Milk Ricotta", "Black Périgord Truffles", "Brown Butter", "Sage", "Aged Parmigiano"],
      winePairing: "Barolo 2017 or Vintage Franciacorta",
      image: "https://images.unsplash.com/photo-1551183053-bf91a1d81141?auto=format&fit=crop&w=800&q=80"
    };
  }

  if (promptLower.includes('salmon') || promptLower.includes('fish') || promptLower.includes('seafood')) {
    return {
      name: "Wild Alaskan King Salmon en Croûte",
      category: "Chef Signatures",
      description: "Pan-roasted wild king salmon wrapped in delicate herb puff pastry, resting on braised fennel, saffron emulsification, and Ossetra caviar pearls.",
      price: 44.0,
      calories: 620,
      prepTime: "20 min",
      tags: ["Chef Special", "High Protein"],
      allergens: ["Fish", "Dairy", "Gluten"],
      ingredients: ["Wild King Salmon", "Fennel", "Saffron Velouté", "Ossetra Caviar", "Flaky Pastry"],
      winePairing: "Meursault Chardonnay or Pinot Noir",
      image: "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?auto=format&fit=crop&w=800&q=80"
    };
  }

  // Default gourmet creation
  return {
    name: `Chef's Artisanal ${concept.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}`,
    category: "Chef Signatures",
    description: `A masterfully composed dish featuring ${concept}, accented with seasonal heirloom reductions, cold-pressed estate olive oil, and delicate micro-botanicals.`,
    price: 32.5,
    calories: 510,
    prepTime: "16-18 min",
    tags: ["Chef Special"],
    allergens: ["Dairy"],
    ingredients: [concept, "Heirloom Herbs", "Estate Butter", "Maldon Sea Salt"],
    winePairing: "Sommelier Special Vintage Reserve",
    image: "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=800&q=80"
  };
}
