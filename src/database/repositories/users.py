"""
* Project Name: BONDVAULT PK

* Description: User table repository operations.

* Author: Wolf4605
* Email: mab4605@gmail.com

* Date: 2026-10-23 07:30:49

* Last Modified by: Wolf4605
* Last Modified time: 2026-10-23 07:38:45

* License: MIT
* Copyright© BondVault PK. All rights reserved.
"""

from typing import cast
from uuid import UUID

from ...models.user_model import UserInfo, UserRegister, UserUpdate
from ...utilities.auth import verify_password
from ..connection import Database
from .base import _Repository, _validate_pagination


class User(_Repository):
    """Registration, profile, verification, and login operations for users."""

    async def register(self, data: UserRegister) -> UserInfo:
        """Create a user and return its non-sensitive fields."""
        record = await self._db.fetchrow(
            """
            INSERT INTO "users" (
                "username", "email", "password_hash", "first_name",
                "last_name", "contact"
            )
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING *
            """,
            data.username,
            data.email,
            data.password_hash,
            data.first_name,
            data.last_name,
            data.contact,
        )
        result = Database._one(UserInfo, record)
        assert result is not None
        return result

    async def get_by_id(self, user_id: UUID | str) -> UserInfo | None:
        """Find a user by its UUID."""
        return cast(
            UserInfo | None,
            Database._one(
                UserInfo,
                await self._db.fetchrow(
                    'SELECT * FROM "users" WHERE "id" = $1',
                    Database._uuid(user_id),
                ),
            ),
        )

    async def get_by_username(self, username: str) -> UserInfo | None:
        """Find a user by its unique username."""
        return cast(
            UserInfo | None,
            Database._one(
                UserInfo,
                await self._db.fetchrow(
                    'SELECT * FROM "users" WHERE "username" = $1',
                    username,
                ),
            ),
        )

    async def authenticate(self, username: str, password: str) -> UserInfo | None:
        """Verify a user's username/email and password without exposing its hash."""
        record = await self._db.fetchrow(
            """
            SELECT * FROM "users"
            WHERE "username" = $1 OR LOWER("email") = LOWER($1)
            ORDER BY ("username" = $1) DESC
            LIMIT 1
            """,
            username,
        )
        if record is None or not verify_password(password, record["password_hash"]):
            return None
        return Database._one(UserInfo, record)

    async def get_by_email(self, email: str) -> UserInfo | None:
        """Find a user by its unique email address."""
        return cast(
            UserInfo | None,
            Database._one(
                UserInfo,
                await self._db.fetchrow(
                    'SELECT * FROM "users" WHERE "email" = $1',
                    email,
                ),
            ),
        )

    async def list(self, *, limit: int = 50, offset: int = 0) -> list[UserInfo]:
        """Return users ordered by account creation, newest first."""
        _validate_pagination(limit, offset)
        return cast(
            list[UserInfo],
            Database._many(
                UserInfo,
                await self._db.fetch(
                    'SELECT * FROM "users" ORDER BY "created_at" DESC LIMIT $1 OFFSET $2',
                    limit,
                    offset,
                ),
            ),
        )

    async def update(self, user_id: UUID | str, data: UserUpdate) -> UserInfo | None:
        """Update user profile fields; omitted fields stay unchanged."""
        record = await self._update(
            "users",
            user_id,
            data.model_dump(exclude_unset=True),
        )
        return cast(UserInfo | None, Database._one(UserInfo, record))

    async def verify(
        self,
        user_id: UUID | str,
        admin_id: UUID | str,
    ) -> UserInfo | None:
        """Mark a user verified by the specified administrator."""
        return cast(
            UserInfo | None,
            Database._one(
                UserInfo,
                await self._db.fetchrow(
                    """
                    UPDATE "users"
                    SET "is_verified" = TRUE, "verified_by" = $2
                    WHERE "id" = $1
                    RETURNING *
                    """,
                    Database._uuid(user_id),
                    Database._uuid(admin_id),
                ),
            ),
        )

    async def record_login(self, user_id: UUID | str) -> bool:
        """Set a user's last-login timestamp to the current database time."""
        return await self._db.fetchval(
            'UPDATE "users" SET "last_login" = CURRENT_TIMESTAMP WHERE "id" = $1 RETURNING TRUE',
            Database._uuid(user_id),
        ) is True

    async def set_password(self, user_id: UUID | str, password_hash: str) -> bool:
        """Replace the stored password hash for an existing user."""
        return await self._db.fetchval(
            'UPDATE "users" SET "password_hash" = $2 WHERE "id" = $1 RETURNING TRUE',
            Database._uuid(user_id),
            password_hash,
        ) is True

    async def delete(self, user_id: UUID | str) -> bool:
        """Delete a user; related bondlists and listings cascade by schema."""
        return await self._db.fetchval(
            'DELETE FROM "users" WHERE "id" = $1 RETURNING TRUE',
            Database._uuid(user_id),
        ) is True
