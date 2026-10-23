"""
* Project Name: BONDVAULT PK

* Description: Contains Models for the User Object of the Project.

* Author: Wolf4605
* Email: mab4605@gmail.com

* Date: 2026-10-22 17:44:12

* Last Modified by: Wolf4605
* Last Modified time: 2026-10-22 17:44:15

* License: MIT
* Copyright© BondVault PK. All rights reserved.
"""
from pydantic import BaseModel, EmailStr, Field, field_validator

from ..utilities.auth import hash_password


class UserRegister(BaseModel):
    """The Model to be used when registering a new `user` to the application."""
    username: str = Field(
        default=...,
        description="`UNIQUE` Identifier of the user.",
        examples=["Wolf_4605", "proximizer", "user123"]
        )
    """`UNIQUE` Identifier of the user."""
    email: EmailStr = Field(
        default=...,
        description="Email Address of the user.",
        examples=["user@example.com", "wolf@example.com", "user@gmail.com"]
        )
    """Email Address of the user."""
    password_hash: str = Field(
        default=...,
        description="Password Hash of the user via Argon2. A normal password can be used and the backend will automatically hash it by using argon2.",
        examples=["YOUR_PASSword", "ChangeMe123!"]
        )
    """Password Hash of the user via Argon2. A normal password can be used and the backend will automatically hash it by using argon2."""
    first_name: str = Field(
        default=...,
        description="First Name of the User.",
        examples=["Awais", "Alice", "Bob"]
        )
    "First Name of the User."
    last_name: str = Field(
        default=...,
        description="Contact Number of the User.",
        examples=["Bilal", "Carter", "Griffin"]
        )
    "Contact Number of the User."
    contact: str = Field(
        default=...,
        description="Contact number of the user.",
        examples=["03121234567", "+923001122344"]
        )
    "Contact number of the user."

    @field_validator("password_hash")
    @classmethod
    def __hash_password(cls, x:str):
        """Hash the user password."""
        return hash_password(x)

    @field_validator("contact")
    @classmethod
    def format_contact(cls, x:str):
        if x.isdigit() and x.startswith("03"):
            return x.replace("0","+92",1)
        else:
            raise ValueError("Invalid Contact Number")