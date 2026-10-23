"""
* Project Name: BONDVAULT PK

* Description: Models for the Prize Bonds, Bondlist and Draw results.

* Author: Wolf4605
* Email: mab4605@gmail.com

* Date: 2026-10-22 19:21:03

* Last Modified by: Wolf4605
* Last Modified time: 2026-10-22 19:21:13

* License: MIT
* Copyright© BondVault PK. All rights reserved.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from ..configs import PrizeBondDenominations
from .base_model import DatabaseModel


class Drawlist(BaseModel):
    draw_date: datetime = Field(
        default=...,
        description="The draw date of the Prize Bond Draw.",
        examples=["2026-10-22 19:30:39.274762"]
    )
    """The draw date of the Prize Bond Draw."""
    denomination: PrizeBondDenominations = Field(
        default=...,
        description="The Bond Denomination for the Pakistani Bonds as issued by National Savings."
        )
    """The Bond Denomination for the Pakistani Bonds as issued by National Savings."""
    first_winner: str = Field(
        default=...,
        description="The first prize winning number from the drawlist as issued by national savings."
    )
    """The first prize winning number from the drawlist as issued by national savings."""
    first_prize: int = Field(
        default=...,
        description="The amount in PKR for the first prize winnner."
    )
    """The amount in PKR for the first prize winnner."""
    second_winner: list[str] = Field(default=..., description="A list of str containing all the second prize winners normally they are upto 3.")
    """A list of str containing all the second prize winners normally they are upto 3."""
    second_prize: int = Field(
        default=...,
        description="The amount in PKR for the second prize winnner."
    )
    """The amount in PKR for the second prize winnner."""
    other_winners: list[str] = Field(default=..., description="A list of str containing all the winning prize numbers.")
    """A list of str containing all the winning prize numbers."""
    other_prize: int =  Field(
        default=...,
        description="The amount in PKR for the second prize winnner."
    )
    """The amount in PKR for the third/normal prize winnner."""


class BondListCreate(BaseModel):
    """The info required when creating a new bondlist."""
    user_id: UUID = Field(default=..., description= "The id of the user this list belongs to.")
    """The id of the user this list belongs to."""
    denomination: PrizeBondDenominations = Field(default=..., description="The denomination of the bonds in this list.")
    """The denomination of the bonds in this list."""

class BondListInfo(BaseModel):
    """The info regarding a user's bondlist."""
    id: UUID = Field(default=..., description="The id of the bondlist.")
    """The id of the bondlist."""
    user_id: UUID = Field(default=..., description= "The id of the user this list belongs to.")
    """The id of the user this list belongs to."""
    denomination: PrizeBondDenominations = Field(default=..., description="The denomination of the bonds in this list.")
    """The denomination of the bonds in this list."""
    bonds: list[str] = Field(default=..., description="A list of Bonds in the bondlist.")
    """A list of Bonds in the bondlist."""

class RegisterBonds(BaseModel):
    """The bond info required when registering a Bond(s)."""
    bond_numbers: list[str] = Field(
        default=...,
        description="A list containing the bond numbers to be added.",
        examples=["000001","[\"000001\",\"000002\",\"000003\"]"]
        )
    """A list containing the bond numbers to be added."""
    bondlist_id: UUID = Field(default=..., description="The bondlist that the bond(s) will belong to.")
    """The bondlist that the bond(s) will belong to."""

    @field_validator("bond_numbers", mode="before")
    @classmethod
    def __map_bondnumbers(cls, x: str | list[str]) -> list[str]:
        if isinstance(x,list):
            return x
        else:
            if isinstance(x, str) and x.isdigit():
                return [x]

            raise ValueError("Invalid Prize Bond Number.")

class BondInfo(BaseModel):
    """The Info regarding the bond."""
    bond_number: str = Field(default=..., description="The number of the physical prize bond.")
    """The number of the physical prize bond."""
    bondlist_id: UUID = Field(default=..., description = "The bondlist id in the database that this bond belongs to.")
    """The bondlist id in the database that this bond belongs to."""
    denomination: PrizeBondDenominations = Field(default=..., description="The denomination of the bond.")
    """The denomination of the bond."""


class BondlistUpdate(BaseModel):
    """Fields that can be changed on a bondlist."""

    denomination: PrizeBondDenominations | None = Field(
        default=None,
        description="The denomination to assign to the bondlist.",
    )


class BondLocation(DatabaseModel):
    """A bond's list and owner, with the applicable denomination."""

    bond_number: str = Field(default=..., description="The number printed on the prize bond.")
    bondlist_id: UUID = Field(default=..., description="The identifier of the bondlist containing this bond.")
    denomination: PrizeBondDenominations = Field(default=..., description="The bond's denomination.")
    user_id: UUID = Field(default=..., description="The identifier of the bondlist owner.")


class DrawlistUpdate(BaseModel):
    """Mutable prize-result fields for an existing drawlist."""

    first_winner: str | None = Field(default=None, description="The first-prize winning bond number.")
    first_prize: int | None = Field(default=None, ge=0, description="The first-prize amount in PKR.")
    second_winner: list[str] | None = Field(default=None, description="The second-prize winning bond numbers.")
    second_prize: int | None = Field(default=None, ge=0, description="The second-prize amount in PKR.")
    other_winners: list[str] | None = Field(default=None, description="The other winning bond numbers.")
    other_prize: int | None = Field(default=None, ge=0, description="The other-prize amount in PKR.")


__all__ = [
    "BondInfo",
    "BondListCreate",
    "BondListInfo",
    "BondLocation",
    "BondlistUpdate",
    "Drawlist",
    "DrawlistUpdate",
    "RegisterBonds",
]