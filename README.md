# LoL Item Shop – Full-Stack CRRUD Project

## Layout
```
app/
  main.py            FastAPI app, includes the router
  database.py        engine + session (SQLite by default; DATABASE_URL to override)
  models.py          Item SQLAlchemy model
  schemas.py         Pydantic request/response schemas
  routers/items.py   the five CRRUD endpoints
frontend/            Flask + Jinja web app (talks to the API over HTTP only)
tests/               pytest tests (conftest.py, test_items.py)
scripts/populate_db.py   sample data
pyproject.toml, requirements.txt
```

# Frontend
Flask + Jinja templates. Every page action is an HTTP call to the API (`API_URL`, default http://localhost:8000):
list → GET /items, detail → GET /items/{id}, create → POST, edit → PUT, delete → DELETE.
Run manually (API must be running): `python frontend/app.py` → http://localhost:5000

## Setup 
in terminal: `python -m venv .venv`, activate it, `pip install -r requirements.txt`

## Run
Run a`python run_all.py`.
- Web app: http://localhost:5000
- API docs: http://localhost:8000/docs

To test `pytest`

## Endpoints
| Operation | Request |
|---|---|
| Create | `POST /items` → 201 |
| Read All | `GET /items?search=&category=&skip=&limit=` |
| Read One | `GET /items/{id}` |
| Update | `PUT /items/{id}` / `PATCH /items/{id}` |
| Delete | `DELETE /items/{id}` → 204 |
