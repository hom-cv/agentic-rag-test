# Agentic RAG Backend

FastAPI, PostgreSQL, and pgvector. Requires Python 3.14 and Pipenv.

Document preprocessing lives in `../data-pipeline/`. Database models and
migrations are maintained here.

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

Set `OPENAI_API_KEY` in `.env` to use `POST /api/v1/retrieval`:

```json
{"question": "What is this project about?", "limit": 5}
```

Returns matching child passages, parent context, source metadata, and cosine
similarity scores. Documents must already be loaded by the pipeline.

Send the same request to `POST /api/v1/chat` for a GPT-5 nano answer using
deduplicated parent passages. Returns `answer` and `sources`, with labels such as
`S1` corresponding to `[S1]` citations. Sources list all supplied context passages.
Each request is independent; chat history is not stored. `limit` counts child matches.

## Migrations

```sh
pipenv run alembic revision --autogenerate -m "describe changes"
# Review the generated migration before applying.
pipenv run alembic upgrade head
```
