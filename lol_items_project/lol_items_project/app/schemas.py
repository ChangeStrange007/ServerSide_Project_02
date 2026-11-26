from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class ItemCategory(str, Enum):
    starter = "starter"
    consumable = "consumable"
    trinket = "trinket"
    boots = "boots"
    basic = "basic"
    epic = "epic"
    legendary = "legendary"
    mythic = "mythic"


class ItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, examples=["Infinity Edge"])
    description: str | None = Field(None, max_length=2000)
    category: ItemCategory
    gold_cost: int = Field(..., ge=0, le=20000, examples=[3400])

    attack_damage: int = Field(0, ge=0)
    ability_power: int = Field(0, ge=0)
    armor: int = Field(0, ge=0)
    magic_resist: int = Field(0, ge=0)
    health: int = Field(0, ge=0)
    mana: int = Field(0, ge=0)
    attack_speed: float = Field(0, ge=0, le=500, description="Percent")
    crit_chance: float = Field(0, ge=0, le=100, description="Percent")
    ability_haste: int = Field(0, ge=0)
    movement_speed: int = Field(0, ge=0)

    passive: str | None = Field(None, max_length=2000)
    is_purchasable: bool = True


class ItemCreate(ItemBase):
    """Body for POST and PUT"""


class ItemUpdate(BaseModel):
    # Body for PATCH
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=2000)
    category: ItemCategory | None = None
    gold_cost: int | None = Field(None, ge=0, le=20000)

    attack_damage: int | None = Field(None, ge=0)
    ability_power: int | None = Field(None, ge=0)
    armor: int | None = Field(None, ge=0)
    magic_resist: int | None = Field(None, ge=0)
    health: int | None = Field(None, ge=0)
    mana: int | None = Field(None, ge=0)
    attack_speed: float | None = Field(None, ge=0, le=500)
    crit_chance: float | None = Field(None, ge=0, le=100)
    ability_haste: int | None = Field(None, ge=0)
    movement_speed: int | None = Field(None, ge=0)

    passive: str | None = Field(None, max_length=2000)
    is_purchasable: bool | None = None


class ItemResponse(ItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
