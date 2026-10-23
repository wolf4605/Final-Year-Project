"""
* Project Name: BONDVAULT PK

* File: undefined
* Description: Utility functions used in logging system.

* Author: Wolf4605
* Email: mab4605@gmail.com

* Date: 2026-10-20 18:28:57

* Last Modified by: Wolf4605
* Last Modified time: 2026-10-21 19:59:29

* License: MIT
* Copyright© BondVault PK. All rights reserved.
"""

import datetime as dt
from datetime import datetime, tzinfo


def get_timezone() -> tzinfo:
    """Get the local timezone."""
    local_tz = datetime.now().astimezone().tzinfo
    return local_tz if local_tz else dt.UTC
