"""Add sample League of Legends items. Usage: python -m scripts.populate_db [--if-empty]"""
import sys

from sqlalchemy import select

from app import models
from app.database import Base, SessionLocal, engine

ITEMS = [
    dict(name="Infinity Edge", category="legendary", gold_cost=3400, attack_damage=80, crit_chance=25,
         description="Massively increases critical strike damage.", passive="Critical strikes deal bonus damage."),
    dict(name="Rabadon's Deathcap", category="legendary", gold_cost=3600, ability_power=140,
         description="Huge Ability Power boost.", passive="Increases your total Ability Power."),
    dict(name="Boots of Swiftness", category="boots", gold_cost=900, movement_speed=60,
         description="Enhanced movement speed.", passive="Slows you less."),
    dict(name="Doran's Blade", category="starter", gold_cost=450, attack_damage=10, health=100,
         description="Great opening item for attackers.", passive="Grants omnivamp."),
    dict(name="Health Potion", category="consumable", gold_cost=50, description="Restores health over time."),
    dict(name="Thornmail", category="epic", gold_cost=2700, armor=70, health=350,
         description="Punishes attackers.", passive="Reflects damage and applies Grievous Wounds."),
    dict(name="Banshee's Veil", category="legendary", gold_cost=3100, ability_power=105, magic_resist=40,
         description="Blocks incoming abilities.", passive="Grants a spell shield."),
    dict(name="Stealth Ward", category="trinket", gold_cost=0, description="Places a hidden ward.",
         is_purchasable=False),
]


def seed(only_if_empty: bool) -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if only_if_empty and db.scalars(select(models.Item).limit(1)).first():
            return
        existing = set(db.scalars(select(models.Item.name)))
        new = [models.Item(**i) for i in ITEMS if i["name"] not in existing]
        db.add_all(new)
        db.commit()
        print(f"Seeded {len(new)} item(s).")


if __name__ == "__main__":
    seed("--if-empty" in sys.argv)
