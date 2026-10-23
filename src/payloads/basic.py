"""
* Project Name: BONDVAULT PK

* Description: Contains the base Payloads on which to build other payloads.

* Author: Wolf4605
* Email: mab4605@gmail.com

* Date: 2026-10-23 13:25:53

* Last Modified by: Wolf4605
* Last Modified time: 2026-10-23 13:25:54

* License: MIT
* Copyright© BondVault PK. All rights reserved.
"""
from pydantic import BaseModel, Field, SecretStr, field_validator

from ..configs import PrizeBondDenominations


class LoginPayload(BaseModel):
    """Credentials submitted to either login endpoint."""

    username: str = Field(min_length=1, max_length=254, description="The account username.")
    password: SecretStr = Field(min_length=1, description="The account password.")

class BondAddPayload(BaseModel):
    """Payload to add bond(s) to a user."""
    bonds: str | list[str] = Field(default=..., description="The prize bond number or a list of prize bond_numbers", examples=["000001", "[\"000001\", \"000002\", \"000003\"]"])
    denomination: PrizeBondDenominations = Field(default=..., description= "The denomination of the prize bond.")
