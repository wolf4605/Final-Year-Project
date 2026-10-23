"""
* Project Name: BONDVAULT PK

* Description: Report table repository operations.

* Author: Wolf4605
* Email: mab4605@gmail.com

* Date: 2026-10-23 07:30:49

* Last Modified by: Wolf4605
* Last Modified time: 2026-10-23 07:38:33

* License: MIT
* Copyright© BondVault PK. All rights reserved.
"""

from typing import Any, cast
from uuid import UUID

from ...models.database_models import ReportCreate, ReportInfo
from ..connection import Database
from .base import _Repository, _validate_pagination


class Report(_Repository):
    """User report submission and administrator resolution operations."""

    async def create(self, data: ReportCreate) -> ReportInfo:
        """Submit a report and return its initial pending state."""
        record = await self._db.fetchrow(
            """
            INSERT INTO "reports" ("reported_by", "subject", "content")
            VALUES ($1, $2, $3)
            RETURNING *
            """,
            data.reported_by,
            data.subject,
            data.content,
        )
        result = Database._one(ReportInfo, record)
        if result is None:
            raise RuntimeError("The report was not returned after insertion.")
        return cast(ReportInfo, result)

    async def get(self, report_id: UUID | str) -> ReportInfo | None:
        """Find a report by UUID."""
        return cast(
            ReportInfo | None,
            Database._one(
                ReportInfo,
                await self._db.fetchrow(
                    'SELECT * FROM "reports" WHERE "id" = $1',
                    Database._uuid(report_id),
                ),
            ),
        )

    async def list(
        self,
        *,
        status: str | None = None,
        reported_by: UUID | str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ReportInfo]:
        """List reports with optional status and submitter filters."""
        _validate_pagination(limit, offset)
        if status is not None and status not in {"pending", "resolved"}:
            raise ValueError("status must be 'pending' or 'resolved'.")
        conditions: list[str] = []
        values: list[Any] = []
        if status is not None:
            values.append(status)
            conditions.append(f'"status" = ${len(values)}')
        if reported_by is not None:
            values.append(Database._uuid(reported_by))
            conditions.append(f'"reported_by" = ${len(values)}')
        where = f'WHERE {" AND ".join(conditions)} ' if conditions else ""
        values.extend([limit, offset])
        query = (
            f'SELECT * FROM "reports" {where}'
            f'ORDER BY "created_at" DESC LIMIT ${len(values) - 1} OFFSET ${len(values)}'
        )
        return cast(
            list[ReportInfo],
            Database._many(ReportInfo, await self._db.fetch(query, *values)),
        )

    async def resolve(
        self,
        report_id: UUID | str,
        admin_id: UUID | str,
        response: str | None = None,
    ) -> ReportInfo | None:
        """Resolve a pending report and record its administrator response."""
        return cast(
            ReportInfo | None,
            Database._one(
                ReportInfo,
                await self._db.fetchrow(
                    """
                    UPDATE "reports"
                    SET "status" = 'resolved', "resolved_at" = CURRENT_TIMESTAMP,
                        "resolved_by" = $2, "response" = $3
                    WHERE "id" = $1 AND "status" = 'pending'
                    RETURNING *
                    """,
                    Database._uuid(report_id),
                    Database._uuid(admin_id),
                    response,
                ),
            ),
        )

    async def delete(self, report_id: UUID | str) -> bool:
        """Delete a report by UUID."""
        return await self._db.fetchval(
            'DELETE FROM "reports" WHERE "id" = $1 RETURNING TRUE',
            Database._uuid(report_id),
        ) is True
