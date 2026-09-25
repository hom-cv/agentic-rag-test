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
PostgreSQL must have pgvector installed. Keyword search uses built-in PostgreSQL
full-text search with an English GIN index; no additional extension is needed.

```sh
pipenv run alembic upgrade head
pipenv run fastapi dev app/main.py
```

API docs: http://localhost:8000/docs

Set `OPENAI_API_KEY` in `.env` to use `POST /api/v1/retrieval`:

```json
{"question": "What is this project about?", "limit": 5}
```

Returns matching child passages, parent context, source metadata, and RRF scores.
Retrieval combines cosine vector search and full-text keyword search (`ts_rank_cd`), fetching at least
20 candidates per search (or four times `limit`). Each ranking contributes
`1 / (60 + rank)`; higher combined scores rank first. Documents must already be
loaded by the pipeline. Scores are no longer cosine similarity values.

Send the same request to `POST /api/v1/chat` for an agentic GPT-5 nano answer.
The model can search (returning full parent passages), read a parent passage, or answer using
source labels such as `[S1]`. Search uses the existing hybrid retrieval and reranker.
`limit` controls the first search; the model can change the query and limit later.
At most three retrieval calls are allowed, followed by a final answer or admission
of missing information. There is no separate verifier.

Returns `answer` and `sources` (all supplied sources, not only cited ones).
Each request is independent; history is not stored. Token-limited model responses
get one retry with a larger budget; repeated failure returns HTTP 502.

## Migrations

```sh
pipenv run alembic revision --autogenerate -m "describe changes"
# Review the generated migration before applying.
pipenv run alembic upgrade head
```
