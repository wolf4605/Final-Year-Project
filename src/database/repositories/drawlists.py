"""
* Project Name: BONDVAULT PK

* Description: Drawlist Repository table repository operations.

* Author: Wolf4605
* Email: mab4605@gmail.com

* Date: 2026-10-23 07:30:49

* Last Modified by: Wolf4605
* Last Modified time: 2026-10-23 07:34:24

* License: MIT
* Copyright© BondVault PK. All rights reserved.
"""

from datetime import datetime
from typing import cast

from ...models.bonds_models import Drawlist, DrawlistUpdate
from ..connection import Database
from .base import _Repository, _validate_pagination


class DrawlistRepository(_Repository):
    """Create, retrieve, update, and delete prize draw results."""

    async def create(self, data: Drawlist) -> Drawlist:
        """Insert a drawlist or replace its result fields on key conflict."""
        record = await self._db.fetchrow(
            """
            INSERT INTO "drawlists" (
                "draw_date", "denomination", "first_winner", "first_prize",
                "second_winner", "second_prize", "other_winners", "other_prize"
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            ON CONFLICT ("draw_date", "denomination") DO UPDATE SET
                "first_winner" = EXCLUDED."first_winner",
                "first_prize" = EXCLUDED."first_prize",
                "second_winner" = EXCLUDED."second_winner",
                "second_prize" = EXCLUDED."second_prize",
                "other_winners" = EXCLUDED."other_winners",
                "other_prize" = EXCLUDED."other_prize"
            RETURNING *
            """,
            data.draw_date,
            int(data.denomination),
            data.first_winner,
            data.first_prize,
            data.second_winner,
            data.second_prize,
            data.other_winners,
            data.other_prize,
        )
        result = Database._one(Drawlist, record)
        if result is None:
            raise RuntimeError("The drawlist was not returned after insertion.")
        return cast(Drawlist, result)

    async def get(
        self,
        draw_date: datetime,
        denomination: int,
    ) -> Drawlist | None:
        """Get one result by its composite draw-date/denomination key."""
        return cast(
            Drawlist | None,
            Database._one(
                Drawlist,
                await self._db.fetchrow(
                    'SELECT * FROM "drawlists" WHERE "draw_date" = $1 AND "denomination" = $2',
                    draw_date,
                    denomination,
                ),
            ),
        )

    async def list(
        self,
        *,
        denomination: int | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Drawlist]:
        """List draw results, optionally filtered by bond denomination."""
        _validate_pagination(limit, offset)
        if denomination is None:
            records = await self._db.fetch(
                'SELECT * FROM "drawlists" ORDER BY "draw_date" DESC LIMIT $1 OFFSET $2',
                limit,
                offset,
            )
        else:
            records = await self._db.fetch(
                'SELECT * FROM "drawlists" WHERE "denomination" = $1 ORDER BY "draw_date" DESC LIMIT $2 OFFSET $3',
                denomination,
                limit,
                offset,
            )
        return cast(list[Drawlist], Database._many(Drawlist, records))

    async def update(
        self,
        draw_date: datetime,
        denomination: int,
        data: DrawlistUpdate,
    ) -> Drawlist | None:
        """Update prize result fields for an existing composite-key row."""
        values = data.model_dump(exclude_unset=True)
        if not values:
            return await self.get(draw_date, denomination)
        assignments = ", ".join(
            f'"{column}" = ${index}'
            for index, column in enumerate(values, start=3)
        )
        record = await self._db.fetchrow(
            f"""
            UPDATE "drawlists" SET {assignments}
            WHERE "draw_date" = $1 AND "denomination" = $2
            RETURNING *
            """,
            draw_date,
            denomination,
            *values.values(),
        )
        return cast(Drawlist | None, Database._one(Drawlist, record))

    async def delete(self, draw_date: datetime, denomination: int) -> bool:
        """Delete one draw result by its composite key."""
        return await self._db.fetchval(
            'DELETE FROM "drawlists" WHERE "draw_date" = $1 AND "denomination" = $2 RETURNING TRUE',
            draw_date,
            denomination,
        ) is True
