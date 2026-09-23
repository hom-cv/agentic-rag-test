# Agentic RAG Backend

FastAPI, PostgreSQL, and pgvector. Requires Python 3.14 and Pipenv.

## Setup

```sh
pipenv sync
cp .env_template .env
```

Set your PostgreSQL credentials in `.env` and create the configured database.
PostgreSQL must have pgvector installed.

```sh
pipenv run alembic upgrade head
pipenv run fastapi dev app/main.py
```

API docs: http://localhost:8000/docs

## Migrations

```sh
pipenv run alembic revision --autogenerate -m "describe changes"
# Review the generated migration before applying.
pipenv run alembic upgrade head
```
