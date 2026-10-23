# Database access

`src.database.wrapper.Database` is the application's basic asynchronous
PostgreSQL wrapper. It owns the `asyncpg` connection pool and exposes raw SQL
operations. Application code issues parameterized SQL directly; there is no
repository layer.

## Organization

- `src/database/wrapper.py` defines `Database` and the shared `DB` instance.
- `src/database/schema/` contains database schema, index, task, function, and
  trigger scripts.
- `src/database/__init__.py` re-exports `DB` and `Database`.

## Pool lifecycle

The shared `DB` is created at import time without opening a connection. The
FastAPI lifespan opens the pool during startup and closes it during shutdown.
For a separate database instance:

```python
from src.database import Database

db = Database(dsn="postgresql://...")
await db.pool_create()
try:
    rows = await db.fetch(
        'SELECT "id", "email" FROM "users" WHERE "username" = $1',
        username,
    )
finally:
    await db.pool_close()
```

Pool size, connection timeout, and command timeout default to the values in
`src.configs.DBConfigs`. Calling a query before creating the pool raises
`ConnectionError`.

## Raw SQL methods

Bind every runtime value using asyncpg's positional parameters (`$1`, `$2`,
etc.). Do not interpolate values into query strings.

| Method | Result | Purpose |
| --- | --- | --- |
| `execute(query, *args)` | `str` | Execute a statement and return PostgreSQL's command status. |
| `fetch(query, *args)` | `list[asyncpg.Record]` | Return all rows. |
| `fetchrow(query, *args)` | `asyncpg.Record \| None` | Return the first row, if any. |
| `fetchval(query, *args, column=0)` | `Any` | Return one value from the first row. |
| `connection()` | async context manager | Acquire and release a pooled connection. |
| `transaction()` | async context manager | Run connection operations atomically. Exceptions roll the transaction back. |
| `check_health()` | `bool` | Check whether `SELECT 1` succeeds. |

Identifiers such as table and column names cannot be bound as SQL values. Keep
any dynamic identifier limited to a fixed, validated allowlist.

`asyncpg.Record` values can be converted into response models with
`Model.model_validate(dict(record))`. The currently used account and auth
models are in `src/models/admin_model.py`, `src/models/user_model.py`, and
`src/models/auth_model.py`. Select only the columns required by the caller,
especially for sensitive fields such as password hashes.

## Schema and models

Schema SQL is maintained in `src/database/schema/`. PostgreSQL constraints
remain authoritative; constraint errors are surfaced by the wrapper rather
than converted into success-shaped results.

The schema stores primary keys as UUIDs and uses plural table names such as
`users` and `admins`. `CREATE TABLE IF NOT EXISTS` does not migrate existing
columns or foreign keys; incompatible existing databases need an explicit
migration.
