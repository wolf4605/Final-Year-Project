"""
* Project Name: BONDVAULT PK

* Description: General function utilities used throughout the application.

* Author: Wolf4605
* Email: mab4605@gmail.com

* Date: 2026-10-20 18:36:18

* Last Modified by: Wolf4605
* Last Modified time: 2026-10-21 19:28:42

* License: MIT
* Copyright© BondVault PK. All rights reserved.
"""

import io
import sys
from typing import cast


class _Console:

    def reconfigure_encoding(self) -> None:
        """Reconfigure the encoding of the console."""
        stdout = cast(io.TextIOWrapper, sys.stdout)
        stderr = cast(io.TextIOWrapper, sys.stderr)
        if hasattr(sys.stdout, "reconfigure"):
            stdout.reconfigure(encoding="utf-8")

        if hasattr(sys.stderr, "reconfigure"):
            stderr.reconfigure(encoding="utf-8")

Console = _Console()