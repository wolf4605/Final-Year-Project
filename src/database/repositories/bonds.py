"""
* Project Name: BONDVAULT PK

* Description: Bondlist table repository operations.

* Author: Wolf4605
* Email: mab4605@gmail.com

* Date: 2026-10-23 07:30:49

* Last Modified by: Wolf4605
* Last Modified time: 2026-10-23 07:37:35

* License: MIT
* Copyright© BondVault PK. All rights reserved.
"""

from typing import cast
from uuid import UUID

from ...models.bonds import BondListCreate, BondListInfo, RegisterBonds
from ...models.database_models import BondlistUpdate, BondLocation
from ..connection import Database
from .base import _Repository


class Bondlist(_Repository):
    """Operations for users' denomination-specific bondlists."""

    async def create(self, data: BondListCreate) -> BondListInfo:
        """Create a bondlist and return it with its current bond numbers."""
        record = await self._db.fetchrow(
            """
            INSERT INTO "bondlists" ("user_id", "denomination")
            VALUES ($1, $2)
            RETURNING "id", "user_id", "denomination"
            """,
            Database._uuid(data.user_id),
            int(data.denomination),
        )
        if record is None:
            raise RuntimeError("The bondlist was not returned after insertion.")
        result = dict(record)
        result["bonds"] = []
        return BondListInfo.model_validate(result)

    async def get(self, bondlist_id: UUID | str) -> BondListInfo | None:
        """Get a bondlist and its bond numbers."""
        record = await self._db.fetchrow(
            """
            SELECT bl."id", bl."user_id", bl."denomination",
                   COALESCE(array_agg(b."bond_number" ORDER BY b."bond_number")
                       FILTER (WHERE b."bond_number" IS NOT NULL), ARRAY[]::VARCHAR[]) AS "bonds"
            FROM "bondlists" AS bl
            LEFT JOIN "bonds" AS b ON b."bondlist_id" = bl."id"
            WHERE bl."id" = $1
            GROUP BY bl."id"
            """,
            Database._uuid(bondlist_id),
        )
        return BondListInfo.model_validate(dict(record)) if record is not None else None

    async def list_for_user(
        self,
        user_id: UUID | str,
    ) -> list[BondListInfo]:
        """List a user's bondlists, including each list's bond numbers."""
        records = await self._db.fetch(
            """
            SELECT bl."id", bl."user_id", bl."denomination",
                   COALESCE(array_agg(b."bond_number" ORDER BY b."bond_number")
                       FILTER (WHERE b."bond_number" IS NOT NULL), ARRAY[]::VARCHAR[]) AS "bonds"
            FROM "bondlists" AS bl
            LEFT JOIN "bonds" AS b ON b."bondlist_id" = bl."id"
            WHERE bl."user_id" = $1
            GROUP BY bl."id"
            ORDER BY bl."denomination"
            """,
            Database._uuid(user_id),
        )
        return [BondListInfo.model_validate(dict(record)) for record in records]

    async def update(
        self,
        bondlist_id: UUID | str,
        data: BondlistUpdate,
    ) -> BondListInfo | None:
        """Change a bondlist's denomination and return its updated data."""
        values = data.model_dump(exclude_unset=True)
        if "denomination" in values and values["denomination"] is not None:
            values["denomination"] = int(values["denomination"])
        record = await self._update("bondlists", bondlist_id, values)
        if record is None:
            return None
        return await self.get(bondlist_id)

    async def delete(self, bondlist_id: UUID | str) -> bool:
        """Delete a bondlist and its bonds."""
        return await self._db.fetchval(
            'DELETE FROM "bondlists" WHERE "id" = $1 RETURNING TRUE',
            Database._uuid(bondlist_id),
        ) is True


class Bond(_Repository):
    """Registration, lookup, transfer, and removal of individual bonds."""

    async def register(self, data: RegisterBonds) -> int:
        """Add one or more bond numbers, ignoring numbers already in the list."""
        inserted = await self._db.fetch(
            """
            INSERT INTO "bonds" ("bondlist_id", "bond_number")
            SELECT $1, bond_number
            FROM unnest($2::VARCHAR[]) AS numbers(bond_number)
            ON CONFLICT ("bondlist_id", "bond_number") DO NOTHING
            RETURNING "bond_number"
            """,
            Database._uuid(data.bondlist_id),
            data.bond_numbers,
        )
        return len(inserted)

    async def list_for_bondlist(self, bondlist_id: UUID | str) -> list[str]:
        """List all bond numbers in a bondlist in ascending order."""
        records = await self._db.fetch(
            'SELECT "bond_number" FROM "bonds" WHERE "bondlist_id" = $1 ORDER BY "bond_number"',
            Database._uuid(bondlist_id),
        )
        return [record["bond_number"] for record in records]

    async def find(self, bond_number: str) -> BondLocation | None:
        """Find the bondlist and denomination containing a bond number."""
        record = await self._db.fetchrow(
            """
            SELECT b."bond_number", b."bondlist_id", bl."denomination", bl."user_id"
            FROM "bonds" AS b
            JOIN "bondlists" AS bl ON bl."id" = b."bondlist_id"
            WHERE b."bond_number" = $1
            """,
            bond_number,
        )
        return cast(BondLocation | None, Database._one(BondLocation, record))

    async def move(
        self,
        bond_number: str,
        source_bondlist_id: UUID | str,
        target_bondlist_id: UUID | str,
    ) -> bool:
        """Move a bond between lists only when the source contains it."""
        source_id = Database._uuid(source_bondlist_id)
        target_id = Database._uuid(target_bondlist_id)
        if source_id == target_id:
            return await self._db.fetchval(
                """
                SELECT TRUE FROM "bonds"
                WHERE "bondlist_id" = $1 AND "bond_number" = $2
                """,
                source_id,
                bond_number,
            ) is True

        async with self._db.transaction() as connection:
            target_denomination = await connection.fetchval(
                'SELECT "denomination" FROM "bondlists" WHERE "id" = $1',
                target_id,
            )
            source_denomination = await connection.fetchval(
                'SELECT "denomination" FROM "bondlists" WHERE "id" = $1',
                source_id,
            )
            if target_denomination is None or source_denomination is None:
                return False
            if target_denomination != source_denomination:
                raise ValueError("A bond can only be moved to a list of the same denomination.")
            source_contains_bond = await connection.fetchval(
                """
                SELECT TRUE FROM "bonds"
                WHERE "bondlist_id" = $1 AND "bond_number" = $2
                FOR UPDATE
                """,
                source_id,
                bond_number,
            )
            if source_contains_bond is not True:
                return False
            await connection.execute(
                """
                INSERT INTO "bonds" ("bondlist_id", "bond_number")
                VALUES ($1, $2)
                ON CONFLICT ("bondlist_id", "bond_number") DO NOTHING
                """,
                target_id,
                bond_number,
            )
            moved = await connection.fetchval(
                """
                DELETE FROM "bonds"
                WHERE "bondlist_id" = $1 AND "bond_number" = $2
                RETURNING TRUE
                """,
                source_id,
                bond_number,
            )
            return moved is True

    async def delete(self, bondlist_id: UUID | str, bond_number: str) -> bool:
        """Remove one bond from a bondlist."""
        return await self._db.fetchval(
            'DELETE FROM "bonds" WHERE "bondlist_id" = $1 AND "bond_number" = $2 RETURNING TRUE',
            Database._uuid(bondlist_id),
            bond_number,
        ) is True

    async def delete_all(self, bondlist_id: UUID | str) -> int:
        """Remove every bond from a list and return the number removed."""
        records = await self._db.fetch(
            'DELETE FROM "bonds" WHERE "bondlist_id" = $1 RETURNING "bond_number"',
            Database._uuid(bondlist_id),
        )
        return len(records)
