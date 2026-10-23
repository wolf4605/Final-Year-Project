"""
* Project Name: BONDVAULT PK

* Description: Market table repository operations.

* Author: Wolf4605
* Email: mab4605@gmail.com

* Date: 2026-10-23 07:30:49

* Last Modified by: Wolf4605
* Last Modified time: 2026-10-23 07:36:37

* License: MIT
* Copyright© BondVault PK. All rights reserved.
"""

from typing import Any, cast
from uuid import UUID

from ...models.market_model import MarketCreate, MarketInfo, MarketUpdate
from ..connection import Database
from .base import _Repository, _validate_pagination


class Market(_Repository):
    """Operations for user-published buy and sell listings."""

    async def create(self, data: MarketCreate) -> MarketInfo:
        """Publish a listing and return its database-generated fields."""
        record = await self._db.fetchrow(
            """
            INSERT INTO "market" ("posted_by", "title", "description", "price", "category")
            VALUES ($1, $2, $3, $4, $5)
            RETURNING *
            """,
            data.posted_by,
            data.title,
            data.description,
            data.price,
            data.category,
        )
        result = Database._one(MarketInfo, record)
        if result is None:
            raise RuntimeError("The market listing was not returned after insertion.")
        return cast(MarketInfo, result)

    async def get(self, listing_id: UUID | str) -> MarketInfo | None:
        """Find a market listing by UUID."""
        return cast(
            MarketInfo | None,
            Database._one(
                MarketInfo,
                await self._db.fetchrow(
                    'SELECT * FROM "market" WHERE "id" = $1',
                    Database._uuid(listing_id),
                ),
            ),
        )

    async def list(
        self,
        *,
        category: str | None = None,
        posted_by: UUID | str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[MarketInfo]:
        """List recent listings, with optional category and owner filters."""
        _validate_pagination(limit, offset)
        conditions: list[str] = []
        values: list[Any] = []
        if category is not None:
            if category not in {"buy", "sell"}:
                raise ValueError("category must be 'buy' or 'sell'.")
            values.append(category)
            conditions.append(f'"category" = ${len(values)}')
        if posted_by is not None:
            values.append(Database._uuid(posted_by))
            conditions.append(f'"posted_by" = ${len(values)}')
        where = f'WHERE {" AND ".join(conditions)} ' if conditions else ""
        values.extend([limit, offset])
        query = (
            f'SELECT * FROM "market" {where}'
            f'ORDER BY "created_at" DESC LIMIT ${len(values) - 1} OFFSET ${len(values)}'
        )
        return cast(
            list[MarketInfo],
            Database._many(MarketInfo, await self._db.fetch(query, *values)),
        )

    async def update(
        self,
        listing_id: UUID | str,
        data: MarketUpdate,
    ) -> MarketInfo | None:
        """Update listing content; omitted fields stay unchanged."""
        record = await self._update(
            "market",
            listing_id,
            data.model_dump(exclude_unset=True),
        )
        return cast(MarketInfo | None, Database._one(MarketInfo, record))

    async def delete(self, listing_id: UUID | str) -> bool:
        """Delete a market listing."""
        return await self._db.fetchval(
            'DELETE FROM "market" WHERE "id" = $1 RETURNING TRUE',
            Database._uuid(listing_id),
        ) is True
