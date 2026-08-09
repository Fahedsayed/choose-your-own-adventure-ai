# Docker Deployment

This repository does not currently include Docker configuration files such as a Dockerfile, docker-compose file, or .dockerignore.

## Docker files/configuration found

- No Dockerfile was found.
- No docker-compose.yml or compose.yaml file was found.
- No Docker-related build instructions were found in the repository documentation.

## Services

The application is currently described as two separate services in the repository docs:

- Backend: FastAPI app served from [backend/main.py](../backend/main.py)
- Frontend: React/Vite app served from [frontend](../frontend)

## Build/run commands

The repository currently documents local development commands rather than Docker commands:

- Backend: `python -m uvicorn main:app --host 127.0.0.1 --port 8000`
- Frontend: `npm run dev -- --host 127.0.0.1 --port 5173`

## Ports

- Backend: port 8000
- Frontend: port 5173

## Environment variables

The backend reads configuration from [backend/core/config.py](../backend/core/config.py) and environment variables such as:

- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`
- `DB_NAME`
- `OPENAI_API_KEY`
- `STORY_PROVIDER`

No secrets should be committed; values should be supplied through environment configuration.

## Frontend/backend communication

The frontend calls the backend through the `/api` prefix. In local development, Vite proxies `/api` to the backend at `http://localhost:8000`.

## Local Docker verification status

Docker-based verification was not possible because the repository currently lacks Docker configuration files.

## Deployment requirements

The repository does not currently define a deployment target or deployment pipeline. Any deployment approach would require adding containerization and environment configuration first.

## Recommended next step

If container deployment is desired, the smallest next step would be to add a Dockerfile for the backend and a separate Dockerfile or build step for the frontend, then define how they communicate over the documented ports.
