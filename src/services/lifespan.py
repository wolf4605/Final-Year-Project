"""
* Project Name: BONDVAULT PK

* Description: The sequence of automated event(s) that are to run in the background while the backend is running.

* Author: Wolf4605
* Email: mab4605@gmail.com

* Date: 2026-10-23 09:20:06

* Last Modified by: Wolf4605
* Last Modified time: 2026-10-23 09:21:14

* License: MIT
* Copyright© BondVault PK. All rights reserved.
"""
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
<<<<<<< HEAD

from fastapi import FastAPI

from ..configs import AdminDBConfigs, AppSettings
from ..database import DB
from ..logging import get_logger, setup_logging
from ..utilities.auth_tokens import validate_jwt_config
from .db_initializor import DB_initializor
=======

from fastapi import FastAPI

from ..configs import AppSettings
from ..database.wrapper import DB
from ..logging import get_logger, setup_logging
from ..utilities.auth_tokens import validate_jwt_config
>>>>>>> 650ab09f5fa893458b064e3f3afe2646e080165a


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Configure logging and manage the shared database connection pool."""

    # Actions to perform when API starts
    # 1. Setup logging
    setup_logging()
    logger = get_logger()
    logger.info("Logging System Configured.")

<<<<<<< HEAD
    if AppSettings.Initialize_Database is True:
        if not AdminDBConfigs.ADMIN_POSTGRES_USER or not AdminDBConfigs.ADMIN_POSTGRES_PASSWORD:
            logger.warning("You have asked for initialization of database but have not provided [cyan]ADMIN_POSTGRES_USER[/] or [cyan]ADMIN_POSTGES_PASSWORD[/] in .env file." )
         
        else:
            await DB_initializor().start()
            logger.info("Database initialized now you can remove [cyan]ADMIN_POSTGRES_USER[/] or [cyan]ADMIN_POSTGES_PASSWORD[/] from .env file.")

    await DB.pool_create()
    validate_jwt_config()
=======
    await DB.pool_create()

    # if AppSettings.Initialize_Database is True:
    #     # 2. Initialize the database.
    #     pass

    validate_jwt_config()
    await DB.pool_create()
>>>>>>> 650ab09f5fa893458b064e3f3afe2646e080165a
    try:
        yield
    finally:
        await DB.pool_close()
