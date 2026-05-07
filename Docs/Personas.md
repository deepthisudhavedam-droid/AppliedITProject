# AI Stylist Project Deliverables


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

## Part 4: Feature List

1. AI Wardrobe Digitization: Automatically categorize clothes from photos. (Source: Persona 1 - Maya)
2. Smart Weather Sync: Adjust suggestions based on real-time local forecast. (Source: Scenario 1)
3. Sustainability Tracker: Tracks "Cost-per-wear" and item usage frequency. (Source: Persona 2 - Alex)
4. Formal Style Recommendations: Suggest interview-ready and presentation-friendly outfits. (Source: Persona 3 - Sara)
5. Outfit Calendar: Plan looks for the week ahead. (Source: Scenario 1)
6. "Refresh" Prompt: Suggestions for items not worn in 30+ days. (Source: Scenario 2)

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
