"""Connection-pool management and low-level PostgreSQL operations."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any, TypeVar, cast
from uuid import UUID

import asyncpg
from pydantic import BaseModel

from .. import configs
from ..logging import get_logger

logger = get_logger()
TypeModel = TypeVar("TypeModel", bound=BaseModel)


class Database:
    """Asynchronous database connection wrapper to manage an asyncpg pool and expose safe, typed database operations.

    Args:
        dsn: PostgreSQL connection string. The configured project DSN is used when omitted.
        min_size: Minimum number of connections kept in the pool.
        max_size: Maximum number of connections allowed in the pool.
        timeout: Seconds allowed for opening a pool connection.
        command_timeout: Optional default timeout for individual commands.
    """

    def __init__(
        self,
        dsn: str,
        *,
        min_connects: int = configs.DBConfigs.DB_MIN_CONNECTIONS,
        max_connects: int = configs.DBConfigs.DB_MAX_CONNECTIONS,
        timeout: float = configs.DBConfigs.DB_TIMEOUT,
        command_timeout: float | None = configs.DBConfigs.DB_COMMAND_TIMEOUT,
    ) -> None:

        if min_connects < 1:
            raise ValueError("min_connects must be 1 or greater than 1.")

        if max_connects < min_connects:
            raise ValueError("max_connects must be greater than min_connects.")

        if timeout <= 0:
            raise ValueError("timeout must be greater than 0.")

        if command_timeout is not None and command_timeout <= 0:
            raise ValueError("command timeout must be greater than 0.")

        self.__dsn = dsn
        self.__min_connects = min_connects
        self.__max_connects = max_connects
        self.__timeout = timeout
        self.__command_timeout = command_timeout
        self.__pool: asyncpg.Pool | None = None
        from .repositories import (
            Admin,
            Blacklist,
            Bond,
            Bondlist,
            DrawlistRepository,
            Market,
            Report,
            User,
        )

        self.Admin = Admin(self)
        self.User = User(self)
        self.Bondlist = Bondlist(self)
        self.Bond = Bond(self)
        self.Drawlist = DrawlistRepository(self)
        self.Market = Market(self)
        self.Report = Report(self)
        self.Blacklist = Blacklist(self)

    @property
    def is_initialized(self) -> bool:
        """Return whether a connection pool currently exists."""
        return self.__pool is not None
    
    @property
    def pool(self) -> asyncpg.Pool:
        """Safe getter to ensure the pool is connected before use."""
        if self.__pool is None:
            raise RuntimeError("Database pool is not initialized. Did you forget to await connect()?")
        return self.__pool

    @staticmethod
    def _validate_query(query: str) -> None:
        """Validate the query to be a string. Rejects empty or non-string queries before contacting PostgreSQL."""

        if not isinstance(query, str):
            raise TypeError(
                f"SQL Query must be a non-empty string. Instead got{type(query)}"
            )
        if not query.strip():
            raise ValueError(
                "SQL Query must be a non-empty string. Instead got an empty string"
            )

    async def pool_create(self) -> None:
        """Create a connection pool if one does not exists."""

        if self.__pool is not None:
            return

        try:
            self.__pool = await asyncpg.create_pool(
                dsn=self.__dsn,
                min_size=self.__min_connects,
                max_size=self.__max_connects,
                timeout=self.__timeout,
                command_timeout=self.__command_timeout,
            )

            logger.success("Connection pool created.")
        except Exception as e:
            self.__pool = None
            raise ConnectionError(
                "Unable to connect to database. Please check your credentials and make sure the database is online."
            ) from e

    async def pool_close(self) -> None:
        """Closes the pool and releases all database connections safely."""

        if self.__pool is None:
            return

        pool: asyncpg.Pool = self.__pool

        try:
            await pool.close()
            self.__pool = None
        except Exception as e:
            raise ConnectionError(
                "Unable to close the PostgreSQL connection pool."
            ) from e

    async def reconnect(self) -> None:
        """Replace the cuurent pool with a newly established one."""

        await self.pool_close()
        await self.pool_create()

    def _require_pool(self) -> asyncpg.Pool:
        """Returns the active connection pool."""

        if self.__pool is None:
            raise ConnectionError("Database is not initialized.")
        else:
            return self.__pool

    @asynccontextmanager
    async def connection(self) -> AsyncGenerator[asyncpg.Connection]:
        """Yield one pooled connection and always return it to the pool."""

        pool = self._require_pool()

        try:
            async with pool.acquire() as raw_connection:
                yield cast(asyncpg.Connection, raw_connection)

        except (
            asyncpg.PostgresError,
            ConnectionError,
            RuntimeError,
            ValueError,
            TimeoutError,
        ):
            raise
        except Exception as e:
            raise ConnectionError(
                "An error occurred while connecting to the database."
            ) from e

    @asynccontextmanager
    async def transaction(self) -> AsyncGenerator[asyncpg.Connection]:
        """
        Yield a connection inside an automatically managed transaction.

        Any exception raised in the context rolls the transaction back. The original exception is preserved so application code can handle it.
        """

        async with self.connection() as connection:
            try:
                if connection:
                    async with connection.transaction():
                        yield connection
            except (
                asyncpg.PostgresError,
                ConnectionError,
                RuntimeError,
                ValueError,
                TimeoutError,
            ):
                raise
            except Exception as e:
                raise ConnectionError(
                    "The database transaction could not be completed."
                ) from e

    async def execute(self, query: str, *args: Any) -> str:
        """Execute a write statement and return asyncpg's status string."""

        self._validate_query(query)
        try:
            async with self.connection() as connection:
                return await connection.execute(query, *args)
        except (
            asyncpg.PostgresError,
            ConnectionError,
            RuntimeError,
            ValueError,
            TimeoutError,
        ):
            raise
        except Exception as e:
            raise RuntimeError("An error occurred while executing the query.") from e

    async def fetch(
        self,
        query: str,
        *args: Any,
    ) -> list[asyncpg.Record]:
        """Execute a query and return all rows as asyncpg records."""

        self._validate_query(query)
        try:
            async with self.connection() as connection:
                return await connection.fetch(query, *args)
        except (
            asyncpg.PostgresError,
            ConnectionError,
            RuntimeError,
            ValueError,
            TimeoutError,
        ):
            raise
        except Exception as e:
            raise RuntimeError("The database query failed.") from e

    async def fetchrow(
        self,
        query: str,
        *args: Any,
    ) -> asyncpg.Record | None:
        """Execute a query and return its first row, if one exists."""

        self._validate_query(query)
        try:
            async with self.connection() as connection:
                return await connection.fetchrow(query, *args)
        except (
            asyncpg.PostgresError,
            ConnectionError,
            RuntimeError,
            ValueError,
            TimeoutError,
        ):
            raise
        except Exception as e:
            raise RuntimeError("The database row query failed.") from e

    async def fetchval(
        self,
        query: str,
        *args: Any,
        column: int = 0,
    ) -> Any:
        """Execute a query and return one column from its first row."""

        self._validate_query(query)
        try:
            async with self.connection() as connection:
                return await connection.fetchval(query, *args, column=column)
        except (
            asyncpg.PostgresError,
            ConnectionError,
            RuntimeError,
            ValueError,
            TimeoutError,
        ):
            raise
        except Exception as e:
            raise RuntimeError("The database value query failed.") from e

    async def check_health(self) -> bool:
        """Check the health of the database."""
        try:
            return await self.fetchval("SELECT 1") == 1
        except (
            asyncpg.PostgresError,
            ConnectionError,
            RuntimeError,
            ValueError,
            TimeoutError,
        ):
            return False

    @staticmethod
    def _uuid(identifier: UUID | str) -> UUID:
        """Validate and convert a textual database identifier to a UUID."""
        return identifier if isinstance(identifier, UUID) else UUID(identifier)

    @staticmethod
    def _one(
        model: type[TypeModel],
        record: asyncpg.Record | None,
    ) -> TypeModel | None:
        """Validate one database row as its public Pydantic model."""
        return model.model_validate(dict(record)) if record is not None else None

    @staticmethod
    def _many(model: type[TypeModel], records: list[asyncpg.Record]) -> list[TypeModel]:
        """Validate database rows as public Pydantic models."""
        return [model.model_validate(dict(record)) for record in records]
