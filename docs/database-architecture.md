# Database Architecture

This document summarizes the backend database design as implemented in the current codebase.

## Database technology

- The runtime configuration uses SQLAlchemy with a database URL from the application settings.
- In normal runtime mode, the app builds a PostgreSQL connection string from environment variables such as `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, and `DB_NAME`.
- The test environment can use SQLite via `DATABASE_URL`.

## Connection and session architecture

The database connection is configured in [backend/db/database.py](../backend/db/database.py):

- `engine` is created with `create_engine(settings.DATABASE_URL)`.
- `SessionLocal` is a SQLAlchemy session factory created with `sessionmaker(...)`.
- `Base` is the shared declarative base for all ORM models.
- `get_db()` opens a session for each request and closes it when the request finishes.

This pattern is used by FastAPI dependency injection in the routers.

## Main models and tables

### Story

Defined in [backend/models/story.py](../backend/models/story.py)

- Table: `stories`
- Fields:
  - `id`
  - `title`
  - `session_id`
  - `created_at`
- Relationship: one `Story` has many `StoryNode` rows.

### StoryNode

Defined in [backend/models/story.py](../backend/models/story.py)

- Table: `story_nodes`
- Fields:
  - `id`
  - `story_id` (foreign key to `stories.id`)
  - `content`
  - `is_root`
  - `is_ending`
  - `is_winning_ending`
  - `options`
- Relationship: each node belongs to one story.

### StoryJob

Defined in [backend/models/job.py](../backend/models/job.py)

- Table: `story_jobs`
- Fields:
  - `job_id`
  - `session_id`
  - `theme`
  - `status`
  - `story_id`
  - `error`
  - `created_at`
  - `completed_at`

## Relationships

- `Story` → `StoryNode`: one-to-many.
- The relationship is expressed with SQLAlchemy `relationship(...)` calls and a foreign key on `StoryNode.story_id`.
- `StoryJob` is not directly linked to `Story` in the ORM model; it stores the generated `story_id` as a plain column value.

## Read-flow example

A read flow is implemented by the complete-story endpoint in [backend/routers/story.py](../backend/routers/story.py).

1. FastAPI receives `GET /api/stories/{story_id}/complete`.
2. The route injects a database session with `Depends(get_db)`.
3. The endpoint runs a query:
   - `db.query(Story).filter(Story.id == story_id).first()`
4. If the story exists, the route loads the related nodes and builds a complete response object.

This is a simple read operation: locate a row in `stories`, then read related rows from `story_nodes`.

## Write-flow example

A write flow is implemented by the story-creation endpoint in [backend/routers/story.py](../backend/routers/story.py).

1. FastAPI receives `POST /api/stories/create`.
2. The route injects a database session with `Depends(get_db)`.
3. The endpoint creates a `StoryJob` object and adds it to the session:
   - `db.add(job)`
4. The session is committed:
   - `db.commit()`
5. A background task later creates a `Story` and `StoryNode` rows through the story generator.

This is the path used to create a new job and later persist generated story content.

## Simple architecture diagram

```text
Frontend
  ↓
FastAPI route
  ↓
Depends(get_db)
  ↓
SQLAlchemy Session
  ↓
ORM Models (Story, StoryNode, StoryJob)
  ↓
Database (PostgreSQL by default)
```

## Key concepts

- Model: a Python class that maps to a database table using SQLAlchemy.
- Table: the actual database collection of rows for a model.
- Database session: the temporary unit of work used to add, update, query, and commit data.
- Query: a request for rows from the database, such as `db.query(Story).filter(...)`.
- Connection: created from `DATABASE_URL` through `create_engine(...)`.
- Data creation: done by creating ORM objects, adding them to a session, and calling `commit()`.
- Data retrieval: done by querying model classes through the active session.
