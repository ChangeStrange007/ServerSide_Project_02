from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Base, engine
from app.routers import items


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup 
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="League of Legends Items API",
    description="CRUD API for League of Legends items (FastAPI + SQLAlchemy + SQLite).",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(items.router)


@app.get("/", tags=["health"])
def root():
    return {"status": "ok", "docs": "/docs"}
