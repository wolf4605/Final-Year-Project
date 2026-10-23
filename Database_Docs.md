# Database Wrapper

`src.database.wrapper.Database` is the asynchronous PostgreSQL interface used by
the application. It manages one `asyncpg` connection pool and exposes
table-specific repositories for the schema in `src/database/schema/`.

## Code organization

- `src/database/connection.py` contains `Database`, pool lifecycle management,
  transactions, and generic query methods.
- `src/database/repositories/base.py` contains shared repository helpers.
- `src/database/repositories/` contains one module per table area:
  `admins.py`, `users.py`, `bonds.py`, `drawlists.py`, `market.py`,
  `reports.py`, and `blacklist.py`.
- `src/database/wrapper.py` re-exports `DB`, `Database`, and the repository
  classes for compatibility with existing imports.

## Setup and lifecycle

```python
from src.database.wrapper import Database
from src.configs import DBConfigs

db = Database(DBConfigs.CONNECTION_STRING)

await db.pool_create()
try:
    account = await db.User.get_by_email("person@example.com")
finally:
    await db.pool_close()
```

The module also exports `DB`, the application-wide `Database` instance. Creating
the instance does not open connections; call `await DB.pool_create()` during
application startup and `await DB.pool_close()` during shutdown. The
`is_initialized` property indicates whether a pool has been created.
`reconnect()` closes the current pool and creates a new one.

The constructor accepts `dsn` and optional pool settings:

```python
Database(
    dsn="postgresql://...",
    min_connects=1,
    max_connects=10,
    timeout=10,
    command_timeout=30,
)
```

The configured connection settings are used for defaults. A pool must be
initialized before repository operations; otherwise a `ConnectionError` is
raised.

## Common database operations

The wrapper exposes the lower-level operations below for application-specific
queries. Values must be passed as parameters (`$1`, `$2`, etc.), never
interpolated into SQL.

| Method | Result | Purpose |
| --- | --- | --- |
| `execute(query, *args)` | `str` | Execute a statement and return PostgreSQL's command status. |
| `fetch(query, *args)` | `list[asyncpg.Record]` | Return all rows. |
| `fetchrow(query, *args)` | `asyncpg.Record \| None` | Return the first row, if any. |
| `fetchval(query, *args, column=0)` | `Any` | Return one value from the first row. |
| `connection()` | async context manager | Acquire and release a pooled connection. |
| `transaction()` | async context manager | Run operations atomically; exceptions roll back. |
| `check_health()` | `bool` | Check whether `SELECT 1` succeeds. |

Driver, connection, and validation errors are raised to the caller. Methods
which look up or update one record return `None` when no matching row exists;
delete methods return `False` when no row was removed.

## Table repositories

Each repository is available as an attribute of `Database`: `Admin`, `User`,
`Bondlist`, `Bond`, `Drawlist`, `Market`, `Report`, and `Blacklist`.
Identifiers can be supplied as `uuid.UUID` values or UUID strings. UUID strings
are validated before being sent to PostgreSQL.

All list methods use newest-first ordering where applicable. User, admin,
market, report, and drawlist list methods accept `limit` (default `50`) and
`offset` (default `0`); limits must be positive and offsets non-negative.

### `admins`

Registration accepts `src.models.admin_model.AdminRegister`; its password
validator hashes the supplied password before insertion. Results use
`AdminInfo`, which never exposes `password_hash`.

| Method | Description |
| --- | --- |
| `Admin.register(data)` | Register an administrator; return its public fields. |
| `Admin.get_by_id(admin_id)` | Look up by UUID. |
| `Admin.get_by_username(username)` | Look up by unique username. |
| `Admin.get_by_email(email)` | Look up by unique email. |
| `Admin.list(limit=50, offset=0)` | Paginate administrators. |
| `Admin.update(admin_id, AdminUpdate(...))` | Update supplied profile/admin fields. |
| `Admin.set_password(admin_id, password_hash)` | Replace the stored password hash. |
| `Admin.delete(admin_id)` | Delete an administrator. |

### `users`

Registration accepts `src.models.user_model.UserRegister`, which validates the
email/contact fields and hashes the supplied password. `UserInfo` excludes the
password hash.

| Method | Description |
| --- | --- |
| `User.register(data)` | Register a user; return public fields. |
| `User.get_by_id(user_id)` | Look up by UUID. |
| `User.get_by_username(username)` | Look up by unique username. |
| `User.get_by_email(email)` | Look up by unique email. |
| `User.list(limit=50, offset=0)` | Paginate users. |
| `User.update(user_id, UserUpdate(...))` | Update supplied profile fields. |
| `User.verify(user_id, admin_id)` | Verify a user and record the administrator. |
| `User.record_login(user_id)` | Set `last_login` to the database's current time. |
| `User.set_password(user_id, password_hash)` | Replace the stored password hash. |
| `User.delete(user_id)` | Delete a user; schema cascades remove their bondlists, listings, and reports. |

`set_password` expects an already hashed value. Hash passwords in the
authentication/application layer before calling it.

### `bondlists`

`Bondlist.create` accepts `src.models.bonds.BondListCreate`; list responses use
`src.models.bonds.BondListInfo` and include the bond numbers.

| Method | Description |
| --- | --- |
| `Bondlist.create(data)` | Create a denomination-specific list for a user. |
| `Bondlist.get(bondlist_id)` | Get one list and its bond numbers. |
| `Bondlist.list_for_user(user_id)` | Get all lists and bond numbers for a user. |
| `Bondlist.update(bondlist_id, BondlistUpdate(...))` | Change a list's denomination. |
| `Bondlist.delete(bondlist_id)` | Delete a list and its bonds. |

The schema enforces one bondlist per user and denomination.

### `bonds`

`Bond.register` accepts `src.models.bonds.RegisterBonds`, which allows one bond
number or a list. It returns the number of newly inserted bonds; duplicates
already in the same list are ignored.

| Method | Description |
| --- | --- |
| `Bond.register(data)` | Add one or more bond numbers to a list. |
| `Bond.list_for_bondlist(bondlist_id)` | Return sorted bond numbers in a list. |
| `Bond.find(bond_number)` | Find a bond's list, denomination, and owner as `BondLocation`. |
| `Bond.move(bond_number, source_bondlist_id, target_bondlist_id)` | Move a bond between lists of the same denomination. |
| `Bond.delete(bondlist_id, bond_number)` | Remove one bond. |
| `Bond.delete_all(bondlist_id)` | Remove all bonds in a list and return the count. |

The move operation is transactional and raises `ValueError` when the source or
target lists have different denominations.

### `drawlists`

Create and update inputs use `src.models.bonds.Drawlist` and
`src.models.database_models.DrawlistUpdate`. Drawlists are identified by their
composite key `(draw_date, denomination)`.

| Method | Description |
| --- | --- |
| `Drawlist.create(data)` | Insert the result or replace result fields on key conflict. |
| `Drawlist.get(draw_date, denomination)` | Get one result by composite key. |
| `Drawlist.list(denomination=None, limit=50, offset=0)` | Paginate all results or filter by denomination. |
| `Drawlist.update(draw_date, denomination, data)` | Update winner/prize fields. |
| `Drawlist.delete(draw_date, denomination)` | Delete one result. |

### `market`

Create/update inputs and returned rows use `MarketCreate`, `MarketUpdate`, and
`MarketInfo` from `src.models.database_models`.

| Method | Description |
| --- | --- |
| `Market.create(data)` | Publish a `buy` or `sell` listing. |
| `Market.get(listing_id)` | Look up a listing. |
| `Market.list(category=None, posted_by=None, limit=50, offset=0)` | Paginate listings with optional category/owner filters. |
| `Market.update(listing_id, data)` | Update supplied listing fields. |
| `Market.delete(listing_id)` | Delete a listing. |

Categories are limited to `buy` and `sell`; prices cannot be negative.

### `reports`

Create and returned records use `ReportCreate` and `ReportInfo`.

| Method | Description |
| --- | --- |
| `Report.create(data)` | Submit a report in `pending` state. |
| `Report.get(report_id)` | Look up a report. |
| `Report.list(status=None, reported_by=None, limit=50, offset=0)` | Paginate and optionally filter by state or submitter. |
| `Report.resolve(report_id, admin_id, response=None)` | Resolve a pending report and record the admin/response. |
| `Report.delete(report_id)` | Delete a report. |

`resolve` returns `None` if the report does not exist or is no longer pending.

### `blacklist`

Create and returned records use `BlacklistCreate` and `BlacklistInfo`. A null
`duration` means the blacklist entry is permanent.

| Method | Description |
| --- | --- |
| `Blacklist.add(data)` | Add an email/contact entry. |
| `Blacklist.find(email=None, contact=None)` | Find matching active entries; at least one criterion is required. |
| `Blacklist.list(limit=50, offset=0)` | Paginate all entries, including expired entries. |
| `Blacklist.update(blacklist_id, BlacklistUpdate(...))` | Update identifying fields or expiry time. |
| `Blacklist.remove(blacklist_id)` | Remove an entry. |
| `Blacklist.purge_expired()` | Remove expired temporary entries and return the count. |

The database trigger associated with permanent entries also removes matching
user accounts. Treat `Blacklist.add` accordingly.

## Pydantic models

Table request and public response models are in `src/models/`:

- Existing registration and domain inputs: `admin_model.AdminRegister`,
  `user_model.UserRegister`, `bonds.BondListCreate`, `bonds.RegisterBonds`,
  and `bonds.Drawlist`.
- Database operation models: `database_models.AdminInfo`, `AdminUpdate`,
  `UserInfo`, `UserUpdate`, `BondlistUpdate`, `BondLocation`, `DrawlistUpdate`,
  `MarketCreate`, `MarketInfo`, `MarketUpdate`, `ReportCreate`, `ReportInfo`,
  `BlacklistCreate`, `BlacklistUpdate`, and `BlacklistInfo`.

Update models use optional fields. Fields omitted from an update are preserved;
explicitly passing `None` requests a SQL `NULL` value where the schema permits
it. Schema constraints (including `NOT NULL`, unique keys, and foreign keys)
remain authoritative and PostgreSQL constraint errors are not suppressed.

## Schema identifier compatibility

The schema stores primary keys as UUIDs. Foreign-key columns referencing users
or administrators are UUIDs as well, and refer to the plural table names
`users` and `admins`. The wrapper accepts UUID strings at its public methods and
converts them to UUID values before database calls. The schema files use
`CREATE TABLE IF NOT EXISTS`; applying the corrected definitions does not
automatically migrate an existing database with incompatible column types or
foreign keys. Existing installations need an explicit migration before using
these repositories.
