# Database Migrations

This repository does not currently use a dedicated migration framework such as Alembic.

## Migration system/tool

- No migration tool is configured in the repository.
- The backend uses SQLAlchemy models directly.
- Schema creation is handled by SQLAlchemy metadata creation.

## Configuration location

There is no Alembic configuration file or migration directory in the repository.

## Existing migration structure

- No migration files were found.
- There is no migration folder under the backend tree.

## Database initialization process

The database is initialized when the application starts in [backend/main.py](../backend/main.py):

- `create_tables()` is called at import time.
- `create_tables()` is defined in [backend/db/database.py](../backend/db/database.py).
- It runs `Base.metadata.create_all(bind=engine)`.

That means the current setup creates tables from the ORM models automatically if they do not already exist.

## Model → Database relationship

- A SQLAlchemy model is a Python class definition that describes the shape of a table.
- The actual database schema is created from that model metadata when `Base.metadata.create_all(...)` runs.
- In this repository, changing a Python model would not automatically produce a migration file; it would simply change the metadata that is used on startup.

## Model vs database schema

- A model is the Python-side definition of a table.
- The database schema is the actual structure inside the database.
- In this repo, the schema is created from the model metadata directly, rather than through versioned migration files.

## Practical takeaway

If a model changes in this project, the developer would need to update the database manually or by re-running the initialization path that creates tables from the current metadata. There is no migration history or migration runner in place.
