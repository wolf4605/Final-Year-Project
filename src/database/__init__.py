"""
* Project Name: BONDVAULT PK

* Description: Contains the database object and functions.

* Author: Wolf4605
* Email: mab4605@gmail.com

* Date: 2026-10-22 15:42:56

* Last Modified by: Wolf4605
* Last Modified time: 2026-10-22 15:42:58

* License: MIT
* Copyright© BondVault PK. All rights reserved.
"""

"""Shared PostgreSQL wrapper and connection pool."""

from .wrapper import DB, Database

__all__ = ["DB", "Database"]