# Choose Your Own Adventure AI

This workspace contains a React/Vite frontend and a FastAPI backend for generating interactive stories.

## Repository structure

- backend/ — FastAPI application, database models, routers, and story-generation logic.
  - main.py — backend entry point and FastAPI app startup.
  - core/ — configuration, Pydantic models, prompts, and story generation helpers.
  - db/ — database setup and session management.
  - routers/ — API endpoints for stories and jobs.
  - schemas/ — request/response schemas.
  - models/ — database and domain models.
- frontend/ — React/Vite client for the story experience.
  - src/ — application UI, routes, and API calls.
  - public/ — static assets.
- README.md — this file, documenting the project structure and startup steps.

## Entry points

- Frontend entry point: frontend/src/main.jsx
- Backend entry point: backend/main.py

## How the app starts

1. The backend starts a FastAPI server on port 8000.
2. The frontend starts a Vite dev server on port 5173.
3. The frontend calls the backend through the /api prefix, and Vite proxies those requests to http://localhost:8000 during local development.

## Run locally

### Backend

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

The frontend should then be available at http://127.0.0.1:5173 and the API docs at http://127.0.0.1:8000/docs.
