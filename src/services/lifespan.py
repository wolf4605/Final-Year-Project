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
from contextlib import asynccontextmanager
from typing import ParamSpecArgs

from ..configs import AppSettings
from ..logging import get_logger, setup_logging


@asynccontextmanager
async def lifespan():

    # Actions to perform when API starts
    # 1. Setup logging
    setup_logging()
    logger = get_logger()
    logger.info("Logging System Configured.")

    if AppSettings.Initialize_Database is True:
        # 2. Initialize the database.
        pass
    
    yield
