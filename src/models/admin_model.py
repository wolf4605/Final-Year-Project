"""
* Project Name: BONDVAULT PK

* Description: 

* Author: Wolf4605
* Email: mab4605@gmail.com

* Date: 2026-10-22 19:01:41

* Last Modified by: Wolf4605
* Last Modified time: 2026-10-22 19:01:43

* License: MIT
* Copyright© BondVault PK. All rights reserved.
"""
from pydantic import BaseModel, EmailStr, Field, field_validator

from ..utilities.auth import hash_password


class AdminRegister(BaseModel):
    """A model to be used when registering an `administrator`."""
    username: str = Field(
            default=...,
            description="`UNIQUE` Identifier of the administrator.",
            examples=["Wolf_4605", "proximizer", "user123"]
            )
    """`UNIQUE` Identifier of the administrator."""
    email: EmailStr = Field(
        default=...,
        description="Email Address of the administrator.",
        examples=["user@example.com", "wolf@example.com", "user@gmail.com"]
        )
    """Email Address of the administrator."""
    password_hash: str = Field(
        default=...,
        description="Password Hash of the administrator via Argon2. A normal password can be used and the backend will automatically hash it by using argon2.",
        examples=["YOUR_PASSword", "ChangeMe123!"]
        )
    """Password Hash of the user via Argon2. A normal password can be used and the backend will automatically hash it by using argon2."""
    first_name: str = Field(
        default=...,
        description="First Name of the administrator.",
        examples=["Awais", "Alice", "Bob"]
        )
    "First Name of the administrator."
    last_name: str = Field(
        default=...,
        description="Contact Number of the administrator.",
        examples=["Bilal", "Carter", "Griffin"]
        )
    "Contact Number of the administrator."
    contact: str = Field(
        default=...,
        description="Contact number of the administrator.",
        examples=["03121234567", "+923001122344"]
        )
    "Contact number of the administrator."

    is_superuser: bool

    @field_validator("password_hash")
    @classmethod
    def __hash_password(cls, x:str):
        """Hash the user password."""
        return hash_password(x)

    @field_validator("contact")
    @classmethod
    def format_contact(cls, x:str):
        """Formatting the contact to start"""
        if x.isdigit() and x.startswith("03") and len(x)==13:
            return x.replace("0","+92",1)
        elif (x.startswith("+92") and x.count('+')==1 
              and 
              x.strip("+").isdigit() and len(x)==13):
            return x
        else:
            raise ValueError("Invalid Contact Number. Please use a valid Pakistani Mobile Operator Number.")