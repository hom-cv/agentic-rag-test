# Backend setup

Run from this directory with Python 3.14:

```sh
pipenv sync
cp .env_template .env
pipenv run fastapi dev app/main.py
```

Edit `.env` to match your local PostgreSQL credentials. The defaults use
`localhost:5432`, user `postgres`, an empty password, and database `agentic_rag`.
Database connections use asyncpg with TLS disabled for local development.

Create the database explicitly once PostgreSQL is running:

```sh
createdb -h localhost -p 5432 -U postgres agentic_rag
```

Adjust the host, port, user, and database arguments to match your settings.
This command does not read `.env`; supply a password when prompted if required.
The application does not create databases or tables. Connections open on first
database use, so startup, `/health`, and `/docs` work before the database exists.
The initial Alembic migration enables the installed pgvector extension before
creating the tables. Migrations are not run automatically.

## Migrations

Alembic uses the same `POSTGRES_*` settings as the app. Run via Pipenv to load `.env`.

```sh
pipenv run alembic revision --autogenerate -m "describe model changes"
pipenv run alembic upgrade head
```

Review generated revisions before applying them. The initial revision creates
`documents`, `chunks`, and their indexes and constraints. Its downgrade removes
those tables but leaves the potentially shared `vector` extension installed.

## Using sessions

Endpoints can request `session: AnnotatedSession` from
`app.api.dependencies.db`. A request receives its own session, which is closed
automatically. Services must explicitly commit successful writes; closing the
session rolls back any uncommitted transaction. For non-request work, use
`async with build_async_session()() as session` from `app.db.session`.
Each concurrent task needs its own session.

The engine checks pooled connections before reuse and is disposed on application
shutdown. Session objects retain loaded attributes after commit.

## Document and chunk models

Import `Documents`, `Chunks`, and `Base` from `app.models` to register both tables.
Both models inherit creation and modification timestamps from the existing base.
UUIDs are generated when rows are inserted through SQLAlchemy.

Documents store a title, source path or URL, and `ingestion_status`: `pending`
(default), `processing`, `completed`, or `failed`. Titles need not be unique.
Chunks store their document ID, zero-based position, text, optional source location
(such as a page or heading), and a required embedding. Positions are unique within
each document. Deleting a document also deletes its chunks.

The embedding column uses an unspecified vector dimension until an embedding model
is selected. Use the same model and dimension for all stored chunks and queries;
fix the column dimension before adding a vector index. Save chunks after generating
their embeddings. Relationships use `lazy="raise"`; explicitly load them with
`selectinload` when needed to avoid implicit database IO in async code.
