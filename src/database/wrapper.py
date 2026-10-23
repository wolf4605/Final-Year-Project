"""
* Project Name: BONDVAULT PK

* Description: 

* Author: Wolf4605
* Email: mab4605@gmail.com

* Date: 2026-10-21 20:33:40

* Last Modified by: Wolf4605
* Last Modified time: 2026-10-23 07:33:38

* License: MIT
* Copyright© BondVault PK. All rights reserved.
""""""Compatibility exports for the database wrapper and repositories."""

from .. import configs
from .connection import Database
from .repositories import (
    Admin,
    Blacklist,
    Bond,
    Bondlist,
    DrawlistRepository,
    Market,
    Report,
    User,
)

DB = Database(dsn=configs.DBConfigs.CONNECTION_STRING)
"""Application-wide database wrapper used by FastAPI backend."""

__all__ = [
    "DB",
    "Admin",
    "Blacklist",
    "Bond",
    "Bondlist",
    "Database",
    "DrawlistRepository",
    "Market",
    "Report",
    "User",
]
