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
Enabling the `vector` extension in this database is deferred until vector storage
is added.

## Using sessions

Endpoints can request `session: AnnotatedSession` from
`app.api.dependencies.db`. A request receives its own session, which is closed
automatically. Services must explicitly commit successful writes; closing the
session rolls back any uncommitted transaction. For non-request work, use
`async with build_async_session()() as session` from `app.db.session`.
Each concurrent task needs its own session.

The engine checks pooled connections before reuse and is disposed on application
shutdown. Session objects retain loaded attributes after commit.
