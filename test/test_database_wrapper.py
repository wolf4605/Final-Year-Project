"""Tests for raw SQL execution through the basic database wrapper."""

import unittest
from typing import Any
from uuid import uuid4

from src.database import Database


class RecordingConnection:
    def __init__(self) -> None:
        self.query: str | None = None
        self.args: tuple[Any, ...] = ()

    async def fetch(self, query: str, *args: Any) -> list[Any]:
        self.query = query
        self.args = args
        return []

    async def fetchrow(self, query: str, *args: Any) -> None:
        self.query = query
        self.args = args
        return None

    async def execute(self, query: str, *args: Any) -> str:
        self.query = query
        self.args = args
        return "UPDATE 1"


class FakeAcquire:
    def __init__(self, connection: RecordingConnection) -> None:
        self.connection = connection

    async def __aenter__(self) -> RecordingConnection:
        return self.connection

    async def __aexit__(self, *_: object) -> None:
        return None


class FakePool:
    def __init__(self, connection: RecordingConnection) -> None:
        self.connection = connection

    def acquire(self) -> FakeAcquire:
        return FakeAcquire(self.connection)


class DatabaseWrapperTests(unittest.IsolatedAsyncioTestCase):
    """Verify that SQL and bound values reach asyncpg unchanged."""

    def setUp(self) -> None:
        self.database = Database("postgresql://localhost/test")
        self.connection = RecordingConnection()
        self.database._pool = FakePool(self.connection)  # type: ignore[assignment]

    async def test_fetch_forwards_parameterized_sql_and_values(self) -> None:
        user_id = uuid4()
        query = 'SELECT "id" FROM "users" WHERE "id" = $1'

        await self.database.fetch(query, user_id)

        self.assertEqual(self.connection.query, query)
        self.assertEqual(self.connection.args, (user_id,))

    async def test_execute_forwards_multiple_bound_values(self) -> None:
        query = 'UPDATE "users" SET "last_login" = $2 WHERE "id" = $1'
        user_id = uuid4()

        result = await self.database.execute(query, user_id, "now")

        self.assertEqual(result, "UPDATE 1")
        self.assertEqual(self.connection.query, query)
        self.assertEqual(self.connection.args, (user_id, "now"))

    async def test_empty_query_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            await self.database.fetch("  ")


if __name__ == "__main__":
    unittest.main()
