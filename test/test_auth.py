"""
* Project Name: BONDVAULT PK

* Description: 

* Author: Wolf4605
* Email: mab4605@gmail.com

* Date: 2026-10-23 11:21:12

* Last Modified by: Wolf4605
* Last Modified time: 2026-10-23 11:54:02

* License: MIT
* Copyright© BondVault PK. All rights reserved.
""""""Tests for JWT authentication and typed FastAPI principal payloads."""

import os
import unittest
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import jwt
from fastapi import FastAPI
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.testclient import TestClient
from starlette.requests import Request
from starlette.responses import Response

from src.models.admin_model import AdminInfo
from src.models.auth_model import AdminLoginResponse, TokenClaims, UserLoginResponse
from src.models.user_model import UserInfo
from src.routers import admin_auth as admin_auth_routes
from src.routers import user_auth as user_auth_routes
from src.routers.admin_auth import router as admin_auth_router
from src.routers.user_auth import router as user_auth_router
from src.utilities import auth_dependencies
from src.utilities.auth import verify_password
from src.utilities.auth_tokens import create_access_token, decode_access_token

TEST_SECRET = "test-signing-key-with-at-least-32-bytes-long"


def _awaited_argument(mock: AsyncMock, index: int) -> object:
    call = mock.await_args
    if call is None:
        raise AssertionError("The mocked database operation was not awaited.")
    return call.args[index]


class AuthTokenTests(unittest.TestCase):
    """Exercise token signing, expiry, roles, and endpoint registration."""

    def test_token_contains_subject_role_and_idle_expiry(self) -> None:
        subject = uuid4()
        with patch.dict(os.environ, {"JWT_SECRET_KEY": TEST_SECRET}):
            token = create_access_token(subject, "user")
            claims = decode_access_token(token)

        self.assertEqual(claims.sub, subject)
        self.assertEqual(claims.role, "user")
        self.assertEqual(claims.exp - claims.iat, 600)
        self.assertIsInstance(claims, TokenClaims)

    def test_token_rejects_modified_signature(self) -> None:
        with patch.dict(os.environ, {"JWT_SECRET_KEY": TEST_SECRET}):
            token = create_access_token(uuid4(), "admin")
            header, payload, signature = token.split(".")
            replacement = "a" if signature[-1] != "a" else "b"
            tampered = f"{header}.{payload}.{signature[:-1]}{replacement}"
            with self.assertRaises(jwt.InvalidTokenError):
                decode_access_token(tampered)

    def test_malformed_password_hash_fails_authentication(self) -> None:
        self.assertFalse(verify_password("password", "not-a-valid-argon2-hash"))

    def test_authentication_endpoints_are_registered(self) -> None:
        app = FastAPI()
        app.include_router(user_auth_router)
        app.include_router(admin_auth_router)
        paths = app.openapi()["paths"]

        self.assertIn("/users/auth/login", paths)
        self.assertIn("/admins/auth/login", paths)
        self.assertIn("/users/me", paths)
        self.assertIn("/admins/me", paths)
        self.assertIn("UserOAuth2", paths["/users/me"]["get"]["security"][0])
        schemes = app.openapi()["components"]["securitySchemes"]
        self.assertEqual(
            schemes["UserOAuth2"]["flows"]["password"]["tokenUrl"],
            "/users/auth/login",
        )
        self.assertEqual(
            schemes["AdminOAuth2"]["flows"]["password"]["tokenUrl"],
            "/admins/auth/login",
        )
        user_login = paths["/users/auth/login"]["post"]
        self.assertEqual(
            user_login["requestBody"]["content"]["application/x-www-form-urlencoded"]["schema"]["$ref"],
            "#/components/schemas/Body_login_user_users_auth_login_post",
        )


class ActivityRenewalTests(unittest.IsolatedAsyncioTestCase):
    """Check that authenticated activity returns a renewed access token."""

    async def test_user_activity_returns_fresh_access_token_header(self) -> None:
        user_id = uuid4()
        payload = UserInfo(
            id=user_id,
            username="test-user",
            email="user@example.com",
            first_name=None,
            last_name=None,
            contact=None,
            created_at=datetime.now(UTC),
            is_verified=False,
            verified_by=None,
            last_login=None,
        )

        with patch.dict(os.environ, {"JWT_SECRET_KEY": TEST_SECRET}):
            issued_at = datetime.now(UTC) - timedelta(minutes=5)
            token = jwt.encode(
                {
                    "sub": str(user_id),
                    "role": "user",
                    "iat": int(issued_at.timestamp()),
                    "exp": int((issued_at + timedelta(minutes=10)).timestamp()),
                    "jti": str(uuid4()),
                },
                TEST_SECRET,
                algorithm="HS256",
            )
            credentials = token
            response = Response()
            fetchrow = AsyncMock(return_value=payload.model_dump())
            with patch.object(
                auth_dependencies.DB,
                "fetchrow",
                fetchrow,
            ):
                resolved_payload = await auth_dependencies.get_current_user(
                    credentials,
                    response,
                )

            refreshed = decode_access_token(response.headers["X-Access-Token"])

        self.assertEqual(resolved_payload, payload)
        self.assertEqual(_awaited_argument(fetchrow, 1), user_id)
        self.assertEqual(refreshed.sub, user_id)
        self.assertEqual(refreshed.role, "user")
        self.assertGreaterEqual(
            refreshed.exp - int(datetime.now(UTC).timestamp()),
            599,
        )
        self.assertEqual(response.headers["X-Access-Token-Expires-In"], "600")

    async def test_user_login_returns_user_info_and_jwt(self) -> None:
        user_id = uuid4()
        user = UserInfo(
            id=user_id,
            username="test-user",
            email="user@example.com",
            first_name=None,
            last_name=None,
            contact=None,
            created_at=datetime.now(UTC),
            is_verified=False,
            verified_by=None,
            last_login=None,
        )

        fetchrow = AsyncMock(
            return_value=user.model_dump() | {"password_hash": "hashed-password"}
        )
        fetchval = AsyncMock(return_value=True)
        with patch.dict(os.environ, {"JWT_SECRET_KEY": TEST_SECRET}):
            with (
                patch.object(user_auth_routes.DB, "fetchrow", fetchrow),
                patch.object(user_auth_routes.DB, "fetchval", fetchval),
                patch.object(user_auth_routes, "verify_password", return_value=True),
            ):
                result = await user_auth_routes.login_user(
                    OAuth2PasswordRequestForm(
                        username="test-user",
                        password="secret",
                    )
                )
            claims = decode_access_token(result.access_token)

        self.assertIsInstance(result, UserLoginResponse)
        self.assertEqual(result.payload, user)
        self.assertEqual(_awaited_argument(fetchrow, 1), "test-user")
        self.assertEqual(_awaited_argument(fetchval, 1), user_id)
        self.assertEqual(claims.sub, user_id)
        self.assertEqual(claims.role, "user")

    async def test_admin_login_returns_admin_info_and_jwt(self) -> None:
        admin_id = uuid4()
        admin = AdminInfo(
            id=admin_id,
            username="test-admin",
            email="admin@example.com",
            first_name=None,
            last_name=None,
            contact=None,
            created_at=datetime.now(UTC),
            is_superuser=True,
        )

        fetchrow = AsyncMock(
            return_value=admin.model_dump() | {"password_hash": "hashed-password"}
        )
        with patch.dict(os.environ, {"JWT_SECRET_KEY": TEST_SECRET}):
            with (
                patch.object(admin_auth_routes.DB, "fetchrow", fetchrow),
                patch.object(admin_auth_routes, "verify_password", return_value=True),
            ):
                result = await admin_auth_routes.login_admin(
                    OAuth2PasswordRequestForm(
                        username="test-admin",
                        password="secret",
                    )
                )
            claims = decode_access_token(result.access_token)

        self.assertIsInstance(result, AdminLoginResponse)
        self.assertEqual(result.payload, admin)
        self.assertEqual(_awaited_argument(fetchrow, 1), "test-admin")
        self.assertEqual(claims.sub, admin_id)
        self.assertEqual(claims.role, "admin")

    def test_user_login_accepts_email_in_oauth_form(self) -> None:
        user_id = uuid4()
        user = UserInfo(
            id=user_id,
            username="test-user",
            email="user@example.com",
            first_name=None,
            last_name=None,
            contact=None,
            created_at=datetime.now(UTC),
            is_verified=False,
            verified_by=None,
            last_login=None,
        )

        app = FastAPI()
        app.include_router(user_auth_router)
        fetchrow = AsyncMock(
            return_value=user.model_dump() | {"password_hash": "hashed-password"}
        )
        fetchval = AsyncMock(return_value=True)
        with (
            patch.dict(os.environ, {"JWT_SECRET_KEY": TEST_SECRET}),
            patch.object(user_auth_routes.DB, "fetchrow", fetchrow),
            patch.object(user_auth_routes.DB, "fetchval", fetchval),
            patch.object(user_auth_routes, "verify_password", return_value=True),
            TestClient(app) as client,
        ):
            response = client.post(
                "/users/auth/login",
                data={"username": "user@example.com", "password": "secret"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(_awaited_argument(fetchrow, 1), "user@example.com")
        self.assertEqual(_awaited_argument(fetchval, 1), user_id)
        self.assertEqual(response.json()["payload"]["id"], str(user_id))
        self.assertEqual(response.json()["token_type"], "bearer")

    def test_admin_login_accepts_email_in_oauth_form(self) -> None:
        admin_id = uuid4()
        admin = AdminInfo(
            id=admin_id,
            username="test-admin",
            email="admin@example.com",
            first_name=None,
            last_name=None,
            contact=None,
            created_at=datetime.now(UTC),
            is_superuser=True,
        )

        app = FastAPI()
        app.include_router(admin_auth_router)
        fetchrow = AsyncMock(
            return_value=admin.model_dump() | {"password_hash": "hashed-password"}
        )
        with (
            patch.dict(os.environ, {"JWT_SECRET_KEY": TEST_SECRET}),
            patch.object(admin_auth_routes.DB, "fetchrow", fetchrow),
            patch.object(admin_auth_routes, "verify_password", return_value=True),
            TestClient(app) as client,
        ):
            response = client.post(
                "/admins/auth/login",
                data={"username": "admin@example.com", "password": "secret"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(_awaited_argument(fetchrow, 1), "admin@example.com")
        self.assertEqual(response.json()["payload"]["id"], str(admin_id))
        self.assertEqual(response.json()["token_type"], "bearer")

    async def test_admin_dependency_returns_admin_info_payload(self) -> None:
        admin_id = uuid4()
        payload = AdminInfo(
            id=admin_id,
            username="test-admin",
            email="admin@example.com",
            first_name=None,
            last_name=None,
            contact=None,
            created_at=datetime.now(UTC),
            is_superuser=True,
        )

        with patch.dict(os.environ, {"JWT_SECRET_KEY": TEST_SECRET}):
            credentials = create_access_token(admin_id, "admin")
            response = Response()
            request = Request(
                {
                    "type": "http",
                    "method": "GET",
                    "path": "/admins/me",
                    "headers": [],
                }
            )
            fetchrow = AsyncMock(return_value=payload.model_dump())
            with patch.object(
                auth_dependencies.DB,
                "fetchrow",
                fetchrow,
            ):
                resolved_payload = await auth_dependencies.get_current_admin(
                    credentials,
                    response,
                    request,
                )

            refreshed = decode_access_token(response.headers["X-Access-Token"])

        self.assertEqual(resolved_payload, payload)
        self.assertEqual(_awaited_argument(fetchrow, 1), admin_id)
        self.assertEqual(request.state.admin_payload, payload)
        self.assertEqual(refreshed.sub, admin_id)
        self.assertEqual(refreshed.role, "admin")


if __name__ == "__main__":
    unittest.main()
