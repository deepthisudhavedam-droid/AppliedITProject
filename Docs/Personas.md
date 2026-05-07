# AI Stylist Project Deliverables


Product vision document
Due Session : 05 may 2026
--------------------------------------
Vision Statment

||

Personal Wardrobe Scanning — Upload photos of your clothes; AI catalogs items by color, style, fit.

Smart Outfit Mixing — AI suggests complete looks using only your existing wardrobe pieces.

Occasion Matching — Input event type (work, party); get tailored combos instantly.

Teparature varient - weather related outfits

Sustainability Focus — Zero new buys — maximize what you own, reduce waste. 

||

## Part 1: Proto-personas

### Persona 1: Maya Chen - The Busy Urban Professional
- **Background:** 28-year-old Marketing Manager.
- **Skills:** High technical proficiency, comfortable with mobile apps and AI.
- **Motivation:** Reduce "decision fatigue" and save time in the morning.
- **Needs:** Quick, weather-appropriate outfit suggestions from her existing wardrobe.
- **Pain Points:** Too many clothes, hard to visualize new combinations.

### Persona 2: Alex Rivera - The Eco-Conscious Minimalist
- **Background:** 24-year-old Graduate Student and environmental activist.
- **Skills:** Moderate tech-savvy, uses sustainability apps.
- **Motivation:** Extend the lifecycle of existing garments; avoid fast fashion.
- **Needs:** Suggestions for "refreshing" old items and tracking "cost-per-wear."
- **Pain Points:** Feeling like they have nothing to wear despite a full closet; guilt about buying new.

### Persona 3: Sara Khan – The Ambitious Professional
- **Background:** 21-year-old final-year college student preparing for internships and corporate interviews.
- **Skills:** Comfortable using fashion, productivity, and scheduling apps for daily planning.
- **Motivation:** Build a confident and professional image while maintaining comfort and simplicity.
- **Needs:** Quick outfit recommendations for formal events, interview-ready combinations, and minimal styling guidance.
- **Pain Points:** Stress while choosing outfits under time pressure; uncertainty about professional dress codes; limited wardrobe options in hostel life.

---

## Part 2: Scenarios

### Scenario 1: Maya's Rainy Workday
- Maya wakes up at 7:15 AM in her Berlin apartment. She has a client presentation at 9:00 AM, and the weather forecast shows unexpected rain and a temperature drop. Standing in front of her overflowing wardrobe, she feels the familiar frustration — too many clothes, no time to think.

She opens your AI Fashion Stylist App, uploads a quick mirror photo, and instantly receives a curated outfit combination from her existing wardrobe that matches her skin tone, the rainy weather, and the formal occasion.

For the first time in weeks, she leaves home without second‑guessing her outfit.

### Scenario 2: Alex's Weekend Upcycling
On a Saturday afternoon in their home office, Alex Rivera used the “Refresh” feature to style a forgotten denim jacket for a friend’s birthday. After uploading the jacket, the AI suggested pairing it with a vintage scarf and black trousers already available in their wardrobe. The result was a stylish new outfit that made Alex feel confident without spending money on new clothes or creating additional waste.
### Scenario 3: Actor: Sara Khan
Goal: Find a professional yet comfortable outfit for her first internship interview.
Setting: Hostel room, 7:00 AM, nervous before interview day.
Action: Sara uses the app’s “Formal” and “Minimal Style” filters for recommendations.
Outcome: She confidently wears a blazer-trouser combination and makes a great first impression.

---

## Part 3: User Stories

### Epic: Wardrobe Management
1. **As a** user, **I want to** upload photos of my clothes **so that** the AI can recognize and categorize them.
2. **As a** user, **I want to** tag items with attributes like "formal" or "summer" **so that** I can filter them easily.

### Epic: AI Recommendations (Broken Down)
1. **As a** busy professional, **I want to** receive outfit suggestions based on the daily weather **so that** I don't have to check multiple apps.
2. **As a** sustainability advocate, **I want to** see which items I haven't worn in a while **so that** I can prioritize using them.
3. **As a** fashion student, **I want** the AI to suggest "bold" combinations **so that** I can experiment with new styles.

---

## Part 4: Feature List

1. AI Wardrobe Digitization: Automatically categorize clothes from photos. (Source: Persona 1 - Maya)
2. Smart Weather Sync: Adjust suggestions based on real-time local forecast. (Source: Scenario 1)
3. Sustainability Tracker: Tracks "Cost-per-wear" and item usage frequency. (Source: Persona 2 - Alex)
4. Formal Style Recommendations: Suggest interview-ready and presentation-friendly outfits. (Source: Persona 3 - Sara)
5. Outfit Calendar: Plan looks for the week ahead. (Source: Scenario 1)
6. "Refresh" Prompt: Suggestions for items not worn in 30+ days. (Source: Scenario 2)
7.Virtual Try-on (V1): Simple overlay of items to visualize the look. (Source: Competitive Analysis/User Needs)

---

## Part 5: Key Trade-offs Debated

**Manual vs. Automatic Tagging:**
The group debated whether to allow users to manually tag every item or rely 100% on AI image recognition.
- **Pros of AI:** Faster, better user experience for Maya (busy professional).
- **Pros of Manual:** More accurate for niche styles (Jordan).
- **Decision:** We chose a **Hybrid Model**. The AI provides "Best Guess" tags which the user can quickly confirm or edit. This balances speed with accuracy.

---

## Part 6: Individual Written Reflections

**Question 1: How did the personas influence your design choices?**
*Answer:* The personas acted as a "north star." For example, we initially didn't prioritize weather integration, but after creating "Maya," it became clear that her primary pain point was morning efficiency, which is heavily dictated by the weather.

**Question 2: What was the most challenging part of deriving user stories from scenarios?**
*Answer:* The challenge was ensuring the stories were "atomic" and didn't overlap too much. We had to break down the "Recommendation" epic into specific stories for weather, style preference, and usage frequency to make them actionable for development.
