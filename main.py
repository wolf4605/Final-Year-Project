"""
* Project Name: BONDVAULT PK

* File: main.py
* Description: 

* Author: Wolf4605
* Email: mab4605@gmail.com

* Date: 2026-10-20 17:39:33

* Last Modified by: Wolf4605
* Last Modified time: 2026-10-21 19:24:42

* License: MIT
* Copyright© BondVault PK. All rights reserved.
"""

import logging
from pathlib import Path

import asyncpg
from fastapi import FastAPI, Request, status
from fastapi.responses import HTMLResponse, JSONResponse
from scalar_fastapi import AgentScalarConfig, Layout, get_scalar_api_reference
from starlette.exceptions import HTTPException as _HTTPException

from src import Tags
from src.configs import AppSettings

# ╔══════════════════════════════════════════════════════════╗
# ║                  CONFIGURING THE LOGGER                  ║
# ╚══════════════════════════════════════════════════════════╝

exception_file_logger = logging.getLogger("application.errors")

# ╔══════════════════════════════════════════════════════════╗
# ║               MAIN APPLICATION ENTRYPOINT                ║
# ╚══════════════════════════════════════════════════════════╝

app = FastAPI(
    title= AppSettings.Title,
    version= AppSettings.Version,
    description= AppSettings.Description,
    terms_of_service=None,
    contact=AppSettings.Contact[0],
    license_info=AppSettings.License,
    openapi_tags = Tags,
    openapi_url="/"
    # lifespan = lifespan
)
"""
The main application variable used to run the Backend.
"""
# ╔══════════════════════════════════════════════════════════╗
# ║                    TESTING ENDPOINTS                     ║
# ╚══════════════════════════════════════════════════════════╝

# To Be removed before final build

@app.get("/health")
async def get_health():

    raise TypeError("Unknown Value")

# ╔══════════════════════════════════════════════════════════╗
# ║                  ROUTERS & MIDDDLEWARE                   ║
# ╚══════════════════════════════════════════════════════════╝


# @app.middleware( middleware_type= "http")
# async def audit_admin_actions(
#     request: Request,
#     call_next: Callable[[Request], Awaitable[Response]]
# ) -> Response:
#     """Audits the results of authenticated administrator API operations."""
#     response: Response = await call_next(request)
#     path: str = request.scope.get("path", "")

#     if path.startswith("/admins/") and path != "/admins/auth/token":
#         admin_id = getattr(
#             request.state,
#             "admin_id",
#             None
#         )
#         client_ip = request.client.host if request.client else None

#         if admin_id is not None and 200 <= response.status_code < 300:
#             auth.audit_admin_actions(
#                 f"{request.method} {path}",
#                 admin_id,
#                 client_ip = client_ip,
#                 status_code = response.status_code
#             )
#         elif response.status_code >= 400:
#             auth.audit_admin_denial(
#                 request.method,
#                 path,
#                 response.status_code,
#                 client_ip = client_ip
#             )

#     return response


# ==================== SCALAR DOCS SETUP ====================

@app.get(
    path= "/",
    include_in_schema=False,
    status_code= 200
)
async def setup_scalar() -> HTMLResponse:
    """
    Overrides the default Swagger UI to a custom Scalar theme.
    """

    css_data:str = f"<head><style>{Path(__file__).parent.joinpath("src").joinpath("static").joinpath("scalar_theme.css").read_text(encoding="utf-8")}</style></head>"
    return get_scalar_api_reference(
        scalar_favicon_url = "https://raw.githubusercontent.com/wolf4605/bondvaultpk.github.io/refs/heads/main/src/assets/logo.svg",
        title= app.title,
        openapi_url= app.openapi_url,
        hide_models= True,
        layout= Layout.MODERN,
        custom_css= css_data,
        agent= AgentScalarConfig(disabled=True)
    )


"""Contains Error Handlers for the Application while it is running."""

# ╔══════════════════════════════════════════════════════════╗
# ║                      ERROR HANDLING                      ║
# ╚══════════════════════════════════════════════════════════╝


def _get_exception_message(error: Exception, fallback: str) -> tuple[str, bool]:
    """Return a safe message and whether the original exception can be formatted."""
    if not error.args:
        return fallback, False

    try:
        message = str(error)
    except IndexError:
        return fallback, False

    return (message or fallback), bool(message)

@app.exception_handler(_HTTPException)
@app.exception_handler(ConnectionError)
@app.exception_handler(TimeoutError)
@app.exception_handler(ValueError)
@app.exception_handler(RuntimeError)
@app.exception_handler(asyncpg.exceptions.PostgresError)
@app.exception_handler(asyncpg.exceptions.InterfaceError)
@app.exception_handler(Exception)
async def handle_app_error(
    request: Request,
    error: ConnectionError|TimeoutError|ValueError|RuntimeError|asyncpg.exceptions.PostgresError|asyncpg.exceptions.InterfaceError|_HTTPException|Exception
) -> JSONResponse:
    """Return"""

    if isinstance(error, _HTTPException):
        status_name = next(
            (
                name
                for name, code in vars(status).items()
                if name.startswith("HTTP_") and code == error.status_code
            ),
            f"HTTP_{error.status_code}"
        )
        return JSONResponse(
            status_code = error.status_code,
            headers = error.headers,
            content= {
                "error" : {
                    "status_code" : error.status_code,
                    "code" : status_name,
                    "message" : error.detail
                }
            }
        )
    elif isinstance(
        error,
        (ConnectionError, asyncpg.exceptions.PostgresConnectionError),
    ):
        status_code = 503
        code = "DATABASE_CONNECTION_FAILURE"
        fallback_message = "The database connection failed."
    elif isinstance(error, (TimeoutError, asyncpg.exceptions.QueryCanceledError)):
        status_code = 504
        code = "TIMEOUT"
        fallback_message = "The database operation timed out."
    elif isinstance(error, asyncpg.exceptions.UniqueViolationError):
        status_code = 409
        code = "DATABASE_CONSTRAINT_VIOLATION"
        fallback_message = "A database constraint was violated."
    elif isinstance(error, ValueError):
        status_code = 400
        code = "INVALID_VALUE"
        fallback_message = "An invalid value was provided."
    elif isinstance(error, RuntimeError):
        status_code = 500
        code = "DATABASE_QUERY_ERROR"
        fallback_message = "The database query failed."
    elif isinstance(error, asyncpg.exceptions.PostgresError):
        status_code = 500
        code = "DATABASE_ERROR"
        fallback_message = "A database error occurred."
    elif isinstance(error, asyncpg.exceptions.InterfaceError):
        status_code = 500
        code = "DATABASE_INTERFACE_ERROR"
        fallback_message = "A database operation could not be completed."
    elif isinstance(error, Exception):
        exception_file_logger.error(
            "Unhandled request exception [%s %s] (%s): %s",
            request.method,
            request.url.path,
            type(error).__name__,
            error,
            exc_info=(type(error), error, error.__traceback__),
        )

        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "status_code": 500,
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred.",
                }
            },
        )
    else:
        raise TypeError(f"Unsupported application error type: {type(error).__name__}")

    message, can_format_exception = _get_exception_message(
        error,
        fallback_message,
    )
    exception_file_logger.error(
        "Request failed [%s %s] (%s, %s): %s",
        request.method,
        request.url.path,
        code,
        type(error).__name__,
        message,
        exc_info=(
            (type(error), error, error.__traceback__) if can_format_exception else None
        ),
    )

    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "status_code": status_code,
                "code": code,
                "message": message,
            }
        },
    )
