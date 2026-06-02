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

_Add your architecture diagram here (C4 Context or Container diagram). Update this as the project evolves._

```
service-a  ──►  service-b
    │
    ▼
  database
```

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Backend | FastAPI (Python) |
| AI Integration | OpenAI API |
| Database | Optional/Can be added later |
| Deployment | Docker & Docker Compose |


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
