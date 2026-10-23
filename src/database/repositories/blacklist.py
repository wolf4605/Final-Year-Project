"""
* Project Name: BONDVAULT PK

* Description: Blacklist table repository operations.

* Author: Wolf4605
* Email: mab4605@gmail.com

* Date: 2026-10-23 07:30:49

* Last Modified by: Wolf4605
* Last Modified time: 2026-10-23 07:34:21

* License: MIT
* Copyright© BondVault PK. All rights reserved.
"""

from typing import cast
from uuid import UUID

from ...models.database_models import BlacklistCreate, BlacklistInfo, BlacklistUpdate
from ..connection import Database
from .base import _Repository, _validate_pagination


class Blacklist(_Repository):
    """Blacklist creation, lookup, listing, and expiry cleanup."""

    async def add(self, data: BlacklistCreate) -> BlacklistInfo:
        """Add a blacklist entry; a null duration represents a permanent entry."""
        record = await self._db.fetchrow(
            """
            INSERT INTO "blacklist" ("email", "contact", "duration")
            VALUES ($1, $2, $3)
            RETURNING *
            """,
            data.email,
            data.contact,
            data.duration,
        )
        result = Database._one(BlacklistInfo, record)
        if result is None:
            raise RuntimeError("The blacklist entry was not returned after insertion.")
        return cast(BlacklistInfo, result)

    async def find(
        self,
        *,
        email: str | None = None,
        contact: str | None = None,
    ) -> list[BlacklistInfo]:
        """Find active blacklist entries by email and/or contact."""
        if email is None and contact is None:
            raise ValueError("Provide an email address, a contact number, or both.")
        conditions: list[str] = []
        values: list[str] = []
        if email is not None:
            values.append(email)
            conditions.append(f'"LOWER("email") = LOWER(${len(values)})')
        if contact is not None:
            values.append(contact)
            conditions.append(f'"contact" = ${len(values)}')
        records = await self._db.fetch(
            f"""
            SELECT * FROM "blacklist"
            WHERE ({" OR ".join(conditions)})
              AND ("duration" IS NULL OR "duration" > CURRENT_TIMESTAMP)
            ORDER BY "created_at" DESC
            """,
            *values,
        )
        return cast(list[BlacklistInfo], Database._many(BlacklistInfo, records))

    async def list(self, *, limit: int = 50, offset: int = 0) -> list[BlacklistInfo]:
        """List blacklist entries, including expired entries, newest first."""
        _validate_pagination(limit, offset)
        return cast(
            list[BlacklistInfo],
            Database._many(
                BlacklistInfo,
                await self._db.fetch(
                    'SELECT * FROM "blacklist" ORDER BY "created_at" DESC LIMIT $1 OFFSET $2',
                    limit,
                    offset,
                ),
            ),
        )

    async def update(
        self,
        blacklist_id: UUID | str,
        data: BlacklistUpdate,
    ) -> BlacklistInfo | None:
        """Update an entry's identity or expiry; omitted values stay unchanged."""
        record = await self._update(
            "blacklist",
            blacklist_id,
            data.model_dump(exclude_unset=True),
        )
        return cast(BlacklistInfo | None, Database._one(BlacklistInfo, record))

    async def remove(self, blacklist_id: UUID | str) -> bool:
        """Remove a blacklist entry by UUID."""
        return await self._db.fetchval(
            'DELETE FROM "blacklist" WHERE "id" = $1 RETURNING TRUE',
            Database._uuid(blacklist_id),
        ) is True

    async def purge_expired(self) -> int:
        """Delete temporary blacklist entries whose expiry time has passed."""
        records = await self._db.fetch(
            'DELETE FROM "blacklist" WHERE "duration" IS NOT NULL AND "duration" <= CURRENT_TIMESTAMP RETURNING "id"'
        )
        return len(records)
