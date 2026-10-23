"""Focused tests for the database wrapper's generated query parameters."""

import unittest
from uuid import uuid4

from src.database.wrapper import Database
from src.models.bonds import RegisterBonds
from src.models.database_models import AdminUpdate


class RecordingDatabase:
    """Capture repository calls without requiring a PostgreSQL server."""

    def __init__(self) -> None:
        self.query: str | None = None
        self.args: tuple[object, ...] = ()

    async def fetch(
        self,
        query: str,
        *args: object,
    ) -> list[dict[str, object]]:
        self.query = query
        self.args = args
        return []

    async def fetchrow(
        self,
        query: str,
        *args: object,
    ) -> None:
        self.query = query
        self.args = args


class DatabaseRepositoryTests(unittest.IsolatedAsyncioTestCase):
    """Test repository behavior that can be validated without a live database."""

    def setUp(self) -> None:
        self.database = Database("postgresql://localhost/test")
        self.recording_database = RecordingDatabase()
        self.database.Market._db = self.recording_database  # type: ignore[assignment]
        self.database.Admin._db = self.recording_database  # type: ignore[assignment]
        self.database.Bond._db = self.recording_database  # type: ignore[assignment]

    async def test_market_filters_use_sequential_placeholders(self) -> None:
        owner_id = uuid4()

        await self.database.Market.list(
            category="sell",
            posted_by=owner_id,
            limit=25,
            offset=10,
        )

        assert self.recording_database.query is not None
        self.assertIn('"category" = $1', self.recording_database.query)
        self.assertIn('"posted_by" = $2', self.recording_database.query)
        self.assertIn("LIMIT $3 OFFSET $4", self.recording_database.query)
        self.assertEqual(
            self.recording_database.args,
            ("sell", owner_id, 25, 10),
        )

    async def test_admin_update_uses_only_model_fields(self) -> None:
        admin_id = uuid4()

        await self.database.Admin.update(
            admin_id,
            AdminUpdate(first_name="Ada", is_superuser=True),
        )

        assert self.recording_database.query is not None
        self.assertIn('"first_name" = $2', self.recording_database.query)
        self.assertIn('"is_superuser" = $3', self.recording_database.query)
        self.assertEqual(
            self.recording_database.args,
            (admin_id, "Ada", True),
        )

    async def test_bond_registration_passes_numbers_as_array(self) -> None:
        bondlist_id = uuid4()

        await self.database.Bond.register(
            RegisterBonds(
                bondlist_id=bondlist_id,
                bond_numbers=["001234", "001235"],
            )
        )

        assert self.recording_database.query is not None
        self.assertIn("unnest($2::VARCHAR[])", self.recording_database.query)
        self.assertEqual(
            self.recording_database.args,
            (bondlist_id, ["001234", "001235"]),
        )


if __name__ == "__main__":
    unittest.main()
