from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(30), index=True, nullable=False)
    gold_cost: Mapped[int] = mapped_column(Integer, nullable=False)

    # Stats
    attack_damage: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    ability_power: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    armor: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    magic_resist: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    health: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    mana: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    attack_speed: Mapped[float] = mapped_column(Float, default=0, nullable=False)  # percent
    crit_chance: Mapped[float] = mapped_column(Float, default=0, nullable=False)  # percent
    ability_haste: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    movement_speed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    passive: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_purchasable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
