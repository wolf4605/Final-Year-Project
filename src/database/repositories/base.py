"""
* Project Name: BONDVAULT PK

* Description: Shared helpers for table repositories.

* Author: Wolf4605
* Email: mab4605@gmail.com

* Date: 2026-10-23 07:30:49

* Last Modified by: Wolf4605
* Last Modified time: 2026-10-23 07:34:10

* License: MIT
* Copyright© BondVault PK. All rights reserved.
"""

from typing import Any
from uuid import UUID

import asyncpg

from ..connection import Database


class _Repository:
    """Common helpers for table-specific database operations."""

    def __init__(self, database: Database) -> None:
        self._db = database

    async def _update(
        self,
        table: str,
        identifier: UUID | str,
        values: dict[str, Any],
    ) -> asyncpg.Record | None:
        """Update allowlisted fields and return the changed row."""
        if not values:
            return await self._db.fetchrow(
                f'SELECT * FROM "{table}" WHERE "id" = $1',
                Database._uuid(identifier),
            )

        assignments = ", ".join(
            f'"{column}" = ${index}'
            for index, column in enumerate(values, start=2)
        )
        query = (
            f'UPDATE "{table}" SET {assignments} '
            'WHERE "id" = $1 RETURNING *'
        )
        return await self._db.fetchrow(
            query,
            Database._uuid(identifier),
            *values.values(),
        )


def _validate_pagination(limit: int, offset: int) -> None:
    """Reject invalid pagination values before issuing a query."""
    if limit < 1:
        raise ValueError("limit must be greater than zero.")
    if offset < 0:
        raise ValueError("offset cannot be negative.")
