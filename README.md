# AI FASHION STYLIST RECOMMANDATION

An AI fashion stylist recommendation should help users get personalized outfit ideas quickly by analyzing their wardrobe, style preferences, weather, and occasion. It should make dressing easier by reducing decision fatigue and showing complete looks that feel practical, confident, and stylish. The strongest recommendation is one that uses clothes the user already owns, so they can create new combinations without buying more. It should also support different needs, such as work outfits, casual looks, formal events, or sustainability goals. Extra value comes from features like wardrobe scanning, virtual try-on, and outfit saving, because they help users visualize choices and plan ahead. In short, an effective AI fashion stylist should be simple, personalized, and useful in everyday life, while still making styling feel creative and fun.


## Team

| Role | Name |
|---|---|
| Product Owner | Deepthi sudha Vedam |
| Scrum Master |Sainath Madhire |
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

## Known Limitations

- API Quota: Gemini free tier: 20 requests/day
- Processing Time: First CLIP inference (~3-5s) loads model; subsequent calls faster
- Image Size: Larger images take longer to process
- Clothing Scope: Best results with clear, well-lit images of single clothing items

## License

MIT License. See LICENSE file for details.
