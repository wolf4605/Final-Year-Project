"""
* Project Name: BONDVAULT PK

* Description: Module Containing all the authentication related functions.

* Author: Wolf4605
* Email: mab4605@gmail.com

* Date: 2026-10-20 19:00:25

* Last Modified by: Wolf4605
* Last Modified time: 2026-10-21 19:30:34

* License: MIT
* Copyright© BondVault PK. All rights reserved.
"""

import argon2
from argon2 import PasswordHasher

_Password_Hasher: PasswordHasher = PasswordHasher()

def hash_password(password: str) -> str:
    """Hash a password using Argon2 Algorithm."""
    return _Password_Hasher.hash(password)


def verify_password(password: str, hash: str) -> bool:
    """Verify a password against a hashed password."""
    try:
        return _Password_Hasher.verify(hash, password)
    except argon2.exceptions.VerifyMismatchError:
        return False
