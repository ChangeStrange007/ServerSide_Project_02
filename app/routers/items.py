from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/items", tags=["items"])


def get_item_or_404(db: Session, item_id: int) -> models.Item:
    item = db.get(models.Item, item_id)
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Item {item_id} not found")
    return item


def commit_or_409(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "An item with that name already exists")


# CREATE
@router.post("", response_model=schemas.ItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(payload: schemas.ItemCreate, db: Session = Depends(get_db)):
    item = models.Item(**payload.model_dump())
    db.add(item)
    commit_or_409(db)
    db.refresh(item)
    return item


# READ ALL
@router.get("", response_model=list[schemas.ItemResponse])
def read_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    category: schemas.ItemCategory | None = None,
    search: str | None = Query(None, description="Case-insensitive name search"),
    db: Session = Depends(get_db),
):
    stmt = select(models.Item).order_by(models.Item.id)
    if category:
        stmt = stmt.where(models.Item.category == category.value)
    if search:
        stmt = stmt.where(models.Item.name.ilike(f"%{search}%"))
    return db.scalars(stmt.offset(skip).limit(limit)).all()


# READ ONE
@router.get("/{item_id}", response_model=schemas.ItemResponse)
def read_item(item_id: int, db: Session = Depends(get_db)):
    return get_item_or_404(db, item_id)


# UPDATE (full replace)
@router.put("/{item_id}", response_model=schemas.ItemResponse)
def replace_item(item_id: int, payload: schemas.ItemCreate, db: Session = Depends(get_db)):
    item = get_item_or_404(db, item_id)
    for field, value in payload.model_dump().items():
        setattr(item, field, value)
    commit_or_409(db)
    db.refresh(item)
    return item


# UPDATE (partial)
@router.patch("/{item_id}", response_model=schemas.ItemResponse)
def update_item(item_id: int, payload: schemas.ItemUpdate, db: Session = Depends(get_db)):
    item = get_item_or_404(db, item_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        if value is None and field in {"name", "category", "gold_cost", "is_purchasable"}:
            raise HTTPException(422, f"{field} cannot be null")
        setattr(item, field, value)
    commit_or_409(db)
    db.refresh(item)
    return item


# DELETE
@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = get_item_or_404(db, item_id)
    db.delete(item)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
