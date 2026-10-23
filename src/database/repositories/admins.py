"""
* Project Name: BONDVAULT PK

* Description: Admin table repository operations.

* Author: Wolf4605
* Email: mab4605@gmail.com

* Date: 2026-10-23 07:30:49

* Last Modified by: Wolf4605
* Last Modified time: 2026-10-23 07:34:06

* License: MIT
* Copyright© BondVault PK. All rights reserved.
"""

from typing import cast
from uuid import UUID

from ...models.admin_model import AdminRegister
from ...models.database_models import AdminInfo, AdminUpdate
from ..connection import Database
from .base import _Repository, _validate_pagination


class Admin(_Repository):
    """CRUD and lookup operations for administrator accounts."""

    async def register(self, data: AdminRegister) -> AdminInfo:
        """Create an administrator and return its non-sensitive fields."""
        record = await self._db.fetchrow(
            """
            INSERT INTO "admins" (
                "username", "email", "password_hash", "first_name",
                "last_name", "contact", "is_superuser"
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING *
            """,
            data.username,
            data.email,
            data.password_hash,
            data.first_name,
            data.last_name,
            data.contact,
            data.is_superuser,
        )
        result = Database._one(AdminInfo, record)
        assert result is not None
        return result

    async def get_by_id(self, admin_id: UUID | str) -> AdminInfo | None:
        """Find an administrator by its UUID."""
        return cast(
            AdminInfo | None,
            Database._one(
                AdminInfo,
                await self._db.fetchrow(
                    'SELECT * FROM "admins" WHERE "id" = $1',
                    Database._uuid(admin_id),
                ),
            ),
        )

    async def get_by_username(self, username: str) -> AdminInfo | None:
        """Find an administrator by its unique username."""
        return cast(
            AdminInfo | None,
            Database._one(
                AdminInfo,
                await self._db.fetchrow(
                    'SELECT * FROM "admins" WHERE "username" = $1',
                    username,
                ),
            ),
        )

    async def get_by_email(self, email: str) -> AdminInfo | None:
        """Find an administrator by its unique email address."""
        return cast(
            AdminInfo | None,
            Database._one(
                AdminInfo,
                await self._db.fetchrow(
                    'SELECT * FROM "admins" WHERE "email" = $1',
                    email,
                ),
            ),
        )

    async def list(self, *, limit: int = 50, offset: int = 0) -> list[AdminInfo]:
        """Return administrators ordered by creation time, newest first."""
        _validate_pagination(limit, offset)
        return cast(
            list[AdminInfo],
            Database._many(
                AdminInfo,
                await self._db.fetch(
                    'SELECT * FROM "admins" ORDER BY "created_at" DESC LIMIT $1 OFFSET $2',
                    limit,
                    offset,
                ),
            ),
        )

    async def update(self, admin_id: UUID | str, data: AdminUpdate) -> AdminInfo | None:
        """Update administrator profile fields; omitted fields stay unchanged."""
        record = await self._update(
            "admins",
            admin_id,
            data.model_dump(exclude_unset=True),
        )
        return cast(AdminInfo | None, Database._one(AdminInfo, record))

    async def set_password(self, admin_id: UUID | str, password_hash: str) -> bool:
        """Replace the stored password hash for an existing administrator."""
        return await self._db.fetchval(
            'UPDATE "admins" SET "password_hash" = $2 WHERE "id" = $1 RETURNING TRUE',
            Database._uuid(admin_id),
            password_hash,
        ) is True

    async def delete(self, admin_id: UUID | str) -> bool:
        """Delete an administrator and report whether a row was removed."""
        return await self._db.fetchval(
            'DELETE FROM "admins" WHERE "id" = $1 RETURNING TRUE',
            Database._uuid(admin_id),
        ) is True
