import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Keep tests off the real database file.
os.environ["DATABASE_URL"] = "sqlite://"

from app.database import Base, get_db 
from app.main import app  


@pytest.fixture()
def client():
    """A TestClient wired to a fresh in-memory database for every test."""
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    # tables are already created on the test engine.
    yield TestClient(app)
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def infinity_edge():
    return {
        "name": "Infinity Edge",
        "description": "Massively increases critical strike damage.",
        "category": "legendary",
        "gold_cost": 3400,
        "attack_damage": 80,
        "crit_chance": 25,
        "passive": "Critical strikes deal bonus damage.",
        "is_purchasable": True,
    }


@pytest.fixture()
def rabadons():
    return {
        "name": "Rabadon's Deathcap",
        "category": "legendary",
        "gold_cost": 3600,
        "ability_power": 140,
    }


@pytest.fixture()
def boots():
    return {
        "name": "Boots of Swiftness",
        "category": "boots",
        "gold_cost": 900,
        "movement_speed": 60,
    }
