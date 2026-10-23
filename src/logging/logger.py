"""
* Project Name: BONDVAULT PK

* Description: Compatibility wrapper for the application logger package.

The implementation is split across dedicated modules for handlers, formatters, and configuration so the logging system remains easy to maintain. This file preserves the public import path used by the rest of the application.

* Author: Wolf4605
* Email: mab4605@gmail.com

* Date: 2026-10-20 18:28:57

* Last Modified by: Wolf4605
* Last Modified time: 2026-10-21 20:08:42

* License: MIT
* Copyright© BondVault PK. All rights reserved.
"""

from .factory import (
    CustomLogger,
    get_logger,
    request_log,
    setup_logging,
    should_log_request,
)

__all__ = [
    "CustomLogger",
    "get_logger",
    "request_log",
    "setup_logging",
    "should_log_request",
]
