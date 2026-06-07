# AI Outfit Finder

A web app that analyzes images and suggests outfit combinations using CLIP vision model for clothing detection and Google Gemini LLM for intelligent outfit recommendations.

## Features

- **Image Analysis**: Upload clothing images and automatically detect attributes (category, color, pattern, style, gender fit)
- **Clothing Detection**: Validates uploaded images contain actual clothing (rejects buildings, landscapes, etc.)
- **Outfit Suggestions**: AI-powered outfit recommendations based on detected clothing attributes
- **Responsive UI**: Modern, drag-and-drop frontend with real-time results
- **Professional Card Display**: Beautiful outfit cards with match percentages, reasoning, and suggested items

## Team

| Role | Name |
|---|---|
| Product Owner | Deepthi sudha Vedam |
| Scrum Master |Sainath Reddy Madhire |
| Developer |Vinay Kumar Komaraboina |
| Developer |Rakshitha Boddu |
| Developer |Pallavi Moulukapuri|
| Developer |Jhanhavi Veerabhadraswamy |

## Project Overview

AI Outfit Finder is a smart web application that analyzes clothing images and recommends stylish outfit combinations using Artificial Intelligence. The system helps users easily select outfits by understanding clothing attributes and generating personalized styling suggestions.

The application contains:

FastAPI backend

AI-powered outfit recommendation system

Simple frontend interface for image upload and outfit display


## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (HTML/JS/CSS)                   │
│                                                                 │
│  [Image Upload] → [Generate Button] → [Results Display]        │
│        ↓                  ↓                    ↓                │
│     FormData          Two-Step API          Outfit Cards       │
│                       Request               with Details        │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ↓ HTTP POST
┌──────────────────────────────────────────────────────────────────┐
│                     FastAPI Backend (Port 8000)                 │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Router: /analyze-image (POST)                           │  │
│  │ ├─ Input: Image file (multipart/form-data)             │  │
│  │ ├─ Process: CLIP Vision Analysis                       │  │
│  │ └─ Output: DetectedData JSON                           │  │
│  └────────────────┬──────────────────────────────────────┘  │
│                   │                                          │
│                   ↓                                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Service: vision.py (CLIP Model)                         │  │
│  │ ├─ is_clothing_image(): Binary classifier              │  │
│  │ │  ├─ Compares clothing vs non-clothing scores        │  │
│  │ │  └─ Rejects non-clothing (buildings, etc.)          │  │
│  │ │                                                      │  │
│  │ └─ _clip_best_label(): Attribute detection           │  │
│  │    ├─ Category (T-shirt, Jacket, etc.)               │  │
│  │    ├─ Color (Black, Blue, etc.)                       │  │
│  │    ├─ Pattern (Solid, Striped, etc.)                  │  │
│  │    ├─ Style (Casual, Formal, etc.)                    │  │
│  │    ├─ Gender (Menswear, Womenswear, Unisex)          │  │
│  │    └─ Fit (Slim, Regular, Oversized, etc.)            │  │
│  └────────────────┬──────────────────────────────────────┘  │
│                   │                                          │
│                   ↓ (Frontend receives DetectedData)          │
│                   │                                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Router: /generate-outfits (POST)                        │  │
│  │ ├─ Input: DetectedData JSON                            │  │
│  │ ├─ Process: Gemini LLM Generation                      │  │
│  │ └─ Output: OutfitResponse with 3 suggestions           │  │
│  └────────────────┬──────────────────────────────────────┘  │
│                   │                                          │
│                   ↓                                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Service: llm.py (Gemini LLM)                            │  │
│  │ ├─ build_prompt(): Format clothing attributes          │  │
│  │ │  └─ Create detailed fashion designer prompt          │  │
│  │ │                                                      │  │
│  │ └─ call_llm(): Query Gemini API                       │  │
│  │    ├─ Model: gemini-2.5-flash                         │  │
│  │    ├─ Max tokens: 4000                                 │  │
│  │    ├─ Response: JSON wrapped in markdown              │  │
│  │    │  ├─ Strip markdown code blocks (```)             │  │
│  │    │  ├─ Repair malformed JSON                        │  │
│  │    │  └─ Parse suggestions array                      │  │
│  │    └─ Return: 3 outfit combinations                   │  │
│  │       ├─ Title, Description                           │  │
│  │       ├─ Match percentage (0-100)                     │  │
│  │       ├─ Reasoning                                    │  │
│  │       ├─ Best occasion                                │  │
│  │       └─ Suggested items (list)                       │  │
│  └────────────────┬──────────────────────────────────────┘  │
│                   │                                          │
└───────────────────┼──────────────────────────────────────────┘
                    │
                    ↓ HTTP Response
┌──────────────────────────────────────────────────────────────┐
│  Frontend Renders Results                                    │
│  ├─ Display detected attributes in tags                     │
│  ├─ Render 3 outfit suggestion cards                        │
│  │  ├─ Title & Description                                │
│  │  ├─ Match % badge (gold accent)                        │
│  │  ├─ Reasoning paragraph                                │
│  │  └─ Suggested items list                               │
│  └─ Scroll to results with animation                        │
└──────────────────────────────────────────────────────────────┘
```

## How It Works

### Step 1: Image Upload & Clothing Detection

1. User uploads an image through the drag-and-drop interface
2. Frontend sends image to `POST /analyze-image`
3. Backend validates content-type (must be `image/*`)
4. **Vision Service (CLIP Model)**:
   - Loads image and converts to RGB
   - Uses OpenCLIP `ViT-B-32` (OpenAI pretrained)
   - Compares image against 19 clothing-related prompts
   - Compares against 10 non-clothing prompts
   - **Classification**: If clothing score > non-clothing score → passes
   - **Rejection**: Otherwise returns error "No clothing detected"

5. If clothing is detected, extracts 6 attributes:
   - **Category**: From 20 types (T-shirt, Jacket, Dress, etc.)
   - **Color**: From 16 colors (Black, Blue, Red, etc.)
   - **Pattern**: From 11 patterns (Solid, Striped, Floral, etc.)
   - **Style**: From 10 styles (Casual, Formal, Streetwear, etc.)
   - **Gender**: From 3 types (Menswear, Womenswear, Unisex)
   - **Fit**: From 8 fits (Slim, Regular, Oversized, etc.)

6. Backend returns `DetectedData` JSON to frontend

### Step 2: Outfit Generation with Gemini LLM

1. Frontend receives detected attributes and sends to `POST /generate-outfits`
2. Backend builds a detailed fashion prompt with all attributes
3. **LLM Service (Google Gemini)**:
   - Calls `gemini-2.5-flash` model
   - Temperature: 0.7 (creative but consistent)
   - Max tokens: 4000 (prevents truncation)
   - Prompt instructs model to create 3 outfit combinations

4. **Response Processing**:
   - Strips markdown code block markers (``` json...```)
   - Repairs malformed JSON (missing braces, trailing commas)
   - Parses suggestions array

5. Each suggestion includes:
   - Title (e.g., "Weekend Wanderer")
   - Description (outfit concept)
   - Match percentage (0-100, relevance to detected item)
   - Reasoning (why this outfit works)
   - Best occasion (when to wear it)
   - Suggested items (list of complementary pieces)

6. Backend returns `OutfitResponse` to frontend

### Step 3: Results Display

1. Frontend receives outfit suggestions
2. Displays detected clothing attributes as tags
3. Renders 3 beautiful cards with:
   - Outfit title in bold
   - Description paragraph
   - Match % badge (gold accent color)
   - Detailed reasoning
   - Bullet list of suggested items
   - Staggered animation (0.1s delay between cards)
4. User can click "Start Over" to upload another image

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | HTML5, CSS3, Vanilla JS | UI, form handling, API communication |
| **Backend** | FastAPI, Uvicorn | REST API, async request handling |
| **Vision** | OpenCLIP (ViT-B-32) | Image-to-text embeddings, clothing detection |
| **LLM** | Google Gemini 2.5 Flash | Outfit suggestion generation |
| **Image Proc** | Pillow (PIL) | Image loading, format conversion |
| **ML Frameworks** | PyTorch, Transformers | CLIP model loading and inference |


## Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose installed
- Git

### Run locally

```bash
gh repo clone deepthisudhavedam-droid/AppliedITProject
cd deepthisudhavedam-droid/AppliedITProject
cp .env.example .env   # fill in your values
docker compose up --build
```

The app will be available at `http://localhost:3000`.

## Repository Structure

```
ai-outfit-finder/
├── README.md
├── backend/
│   ├── main.py                 # FastAPI app initialization, CORS
│   ├── requirements.txt         # Python dependencies
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py          # Pydantic schemas (DetectedData, OutfitSuggestion, OutfitResponse)
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── analyze.py          # POST /analyze-image endpoint
│   │   └── outfits.py          # POST /generate-outfits endpoint
│   └── services/
│       ├── __init__.py
│       ├── vision.py           # CLIP model, clothing detection, attribute extraction
│       └── llm.py              # Gemini LLM integration, prompt building, JSON parsing
│
└── frontend/
    ├── index.html              # UI structure, form, results grid
    ├── script.js               # Event handlers, API calls, result rendering
    └── style.css               # Responsive design, card animations
```

## Documentation

- [Vision Document](docs/vision.md)
- [Persona](docs/Personas.md)
- [Scenarios](docs/Scenarios)
- [User stories](docs/User%20stories)

## Requirements

- Python 3.10+ (recommended 3.11 or newer)
- PyTorch with CUDA support (optional, uses CPU if unavailable)
- See `backend/requirements.txt` for all dependencies

## Environment

Set your Gemini API key before running:

```powershell
$env:GEMINI_API_KEY = 'ya29.your_gemini_api_key_here'
```

Get a key from [Google AI Studio](https://ai.google.dev/)

**Note**: Free tier has 20 requests/day limit. Upgrade to paid plan for higher quotas.

## Setup & Run

**Backend**:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:GEMINI_API_KEY = 'ya29.your_gemini_api_key_here'
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend**:

```bash
cd frontend
python -m http.server 5500
# Open http://localhost:5500 in browser
```

Or open `frontend/index.html` directly in your browser.

## API Endpoints

### POST /analyze-image
Analyzes an uploaded image and detects clothing attributes.

**Request:**
- Content-Type: `multipart/form-data`
- Body: `file` (image file)

**Response (200 OK):**
```json
{
  "category": "Shirt",
  "color": "Blue",
  "pattern": "Solid",
  "style": "Casual",
  "gender": "Menswear",
  "fit": "Regular"
}
```

**Error Response (400 Bad Request):**
```json
{
  "detail": "No clothing detected. Please upload a photo of a shirt, pant, dress, jacket, or clothing on a hanger/person."
}
```

### POST /generate-outfits
Generates outfit suggestions based on detected clothing attributes.

**Request:**
```json
{
  "category": "Shirt",
  "color": "Blue",
  "pattern": "Solid",
  "style": "Casual",
  "gender": "Menswear",
  "fit": "Regular"
}
```

**Response (200 OK):**
```json
{
  "detected": {
    "category": "Shirt",
    "color": "Blue",
    "pattern": "Solid",
    "style": "Casual",
    "gender": "Menswear",
    "fit": "Regular"
  },
  "suggestions": [
    {
      "title": "Weekend Wanderer",
      "description": "A classic casual combination...",
      "match_percentage": 95,
      "reasoning": "Dark wash jeans pair perfectly...",
      "best_occasion": "Weekend errands, casual brunch...",
      "suggested_items": ["Dark Wash Jeans", "White Sneakers", "Blue Watch"]
    },
    ...
  ]
}
```
### Recent Improvements

## Image Analysis

✅ Enhanced clothing detection with margin-based comparison

✅ Support for hanger-displayed items and person-worn clothing

✅ Robust rejection of non-clothing images (buildings, landscapes)

## Outfit Generation

✅ Increased token limit to 4000 (prevents response truncation)

✅ Advanced JSON repair (fixes malformed responses, adds missing braces)

✅ Markdown stripping for properly wrapped responses

✅ Better error logging and user feedback

## Frontend

✅ Detailed error messages from backend (shown to user)

✅ Beautiful responsive card layout with animations

✅ Smooth scrolling to results section

✅ Real-time loading spinner during API calls

## Backend

✅ CORS enabled for all origins

✅ Comprehensive logging for debugging

✅ Graceful error handling with user-friendly messages

✅ Content-type validation for image uploads

## Development

- Logs are printed to console (stderr) during development
- Use uvicorn --reload to auto-restart on code changes
- Frontend updates instantly (no build step needed)
- Check browser console (F12) for frontend errors
- Check backend terminal for API/model logs

## Contributing

Contributions welcome! Please: 1. Test locally before submitting changes 2. Include error handling and logging 3. Document any new environment variables 4. Keep frontend/backend separation clean

## Known Limitations

- API Quota: Gemini free tier: 20 requests/day
- Processing Time: First CLIP inference (~3-5s) loads model; subsequent calls faster
- Image Size: Larger images take longer to process
- Clothing Scope: Best results with clear, well-lit images of single clothing items

## License

MIT License. See LICENSE file for details.
