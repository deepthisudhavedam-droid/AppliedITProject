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
| Database | Optional/Can be added later |
| Deployment | Docker & Docker Compose |
| AI Integration | OpenAI API |

## Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose installed
- Git

### Run locally

```bash
git clone https://github.com/<your-org>/<your-repo>.git
cd <your-repo>
cp .env.example .env   # fill in your values
docker compose up --build
```

The app will be available at `http://localhost:3000`.

## Repository Structure

```
├── README.md
├── .gitignore
├── docs/
│   └── vision.md            # Product vision, personas, user stories
├── services/
│   ├── service-a/           # First microservice
│   └── service-b/           # Second microservice
└── docker-compose.yml
```

## Documentation

- [Vision Document](docs/vision.md)
- [Persona](docs/Personas.md)
- [Scenarios](docs/Scenarios)
- [User stories](docs/User%20stories)

## License

MIT
