import os

import requests
from flask import Flask, abort, flash, redirect, render_template, request, url_for

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-change-me")

# The frontend only ever talks to the backend over HTTP; it has no DB access.
API_URL = os.getenv("API_URL", "http://localhost:8000").rstrip("/")
TIMEOUT = 10
PER_PAGE = 20

CATEGORIES = ["starter", "consumable", "trinket", "boots", "basic", "epic", "legendary", "mythic"]

STATS = [
    ("attack_damage", "Attack Damage", "", False),
    ("ability_power", "Ability Power", "", False),
    ("armor", "Armor", "", False),
    ("magic_resist", "Magic Resist", "", False),
    ("health", "Health", "", False),
    ("mana", "Mana", "", False),
    ("attack_speed", "Attack Speed", "%", True),
    ("crit_chance", "Critical Strike Chance", "%", True),
    ("ability_haste", "Ability Haste", "", False),
    ("movement_speed", "Movement Speed", "", False),
]


class APIUnavailable(Exception):
    pass


def api(method, path, **kwargs):
    # Send an HTTP request to the backend API.
    try:
        return requests.request(method, f"{API_URL}{path}", timeout=TIMEOUT, **kwargs)
    except requests.RequestException:
        raise APIUnavailable()


def api_errors(resp):
    # Turn an API error response into a list of readable messages
    try:
        detail = resp.json().get("detail")
    except ValueError:
        detail = None
    if isinstance(detail, str):
        return [detail]
    if isinstance(detail, list):  # FastAPI validation errors
        msgs = []
        for err in detail:
            field = ".".join(str(p) for p in err.get("loc", []) if p != "body")
            msgs.append(f"{field}: {err.get('msg', 'invalid value')}" if field else err.get("msg", "invalid"))
        return msgs
    return [f"API returned HTTP {resp.status_code}"]


def form_to_payload(form):
    # Build the JSON body for the API from submitted form data

    def num(key, cast, blank):
        raw = (form.get(key) or "").strip()
        if raw == "":
            return blank
        try:
            return cast(raw)
        except ValueError:
            return raw  # let the validation reject it with a message

    payload = {
        "name": (form.get("name") or "").strip(),
        "description": (form.get("description") or "").strip() or None,
        "category": form.get("category") or None,
        "gold_cost": num("gold_cost", int, None),
        "passive": (form.get("passive") or "").strip() or None,
        "is_purchasable": "is_purchasable" in form,
    }
    for key, _label, _suffix, is_float in STATS:
        payload[key] = num(key, float if is_float else int, 0)
    return payload


@app.context_processor
def inject_globals():
    return {"STATS": STATS, "CATEGORIES": CATEGORIES}


@app.errorhandler(APIUnavailable)
def handle_api_down(_e):
    return render_template(
        "error.html", title="API unavailable",
        message=f"Could not reach the backend API at {API_URL}. Is it running?",
    ), 503


@app.errorhandler(404)
def handle_404(_e):
    return render_template("error.html", title="Not found", message="That page or item doesn't exist."), 404


# READ ALL
@app.get("/")
def index():
    page = max(request.args.get("page", 1, type=int), 1)
    category = request.args.get("category", "")
    search = request.args.get("search", "").strip()

    params = {"skip": (page - 1) * PER_PAGE, "limit": PER_PAGE + 1}  # +1 to see a next page
    if category:
        params["category"] = category
    if search:
        params["search"] = search

    resp = api("GET", "/items", params=params)
    items = []
    if resp.ok:
        items = resp.json()
    else:
        for msg in api_errors(resp):
            flash(msg, "error")

    has_next = len(items) > PER_PAGE
    return render_template(
        "index.html", items=items[:PER_PAGE], page=page, has_next=has_next,
        category=category, search=search,
    )


# READ ONE
@app.get("/items/<int:item_id>")
def detail(item_id):
    resp = api("GET", f"/items/{item_id}")
    if resp.status_code == 404:
        abort(404)
    if not resp.ok:
        flash(" ".join(api_errors(resp)), "error")
        return redirect(url_for("index"))
    return render_template("detail.html", item=resp.json())


# CREATE
@app.route("/items/new", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        payload = form_to_payload(request.form)
        resp = api("POST", "/items", json=payload)
        if resp.status_code == 201:
            flash(f"Created “{resp.json()['name']}”.", "success")
            return redirect(url_for("detail", item_id=resp.json()["id"]))
        return render_template("form.html", item=payload, errors=api_errors(resp), mode="create"), 400
    return render_template("form.html", item={"is_purchasable": True}, errors=[], mode="create")


# UPDATE
@app.route("/items/<int:item_id>/edit", methods=["GET", "POST"])
def edit(item_id):
    if request.method == "POST":
        payload = form_to_payload(request.form)
        resp = api("PUT", f"/items/{item_id}", json=payload)
        if resp.ok:
            flash("Item updated.", "success")
            return redirect(url_for("detail", item_id=item_id))
        if resp.status_code == 404:
            abort(404)
        payload["id"] = item_id
        return render_template("form.html", item=payload, errors=api_errors(resp), mode="edit"), 400

    resp = api("GET", f"/items/{item_id}")
    if resp.status_code == 404:
        abort(404)
    if not resp.ok:
        flash(" ".join(api_errors(resp)), "error")
        return redirect(url_for("index"))
    return render_template("form.html", item=resp.json(), errors=[], mode="edit")


# DELETE 
@app.post("/items/<int:item_id>/delete")
def delete(item_id):
    resp = api("DELETE", f"/items/{item_id}")
    if resp.status_code == 204:
        flash("Item deleted.", "success")
    elif resp.status_code == 404:
        flash("That item no longer exists.", "error")
    else:
        flash(" ".join(api_errors(resp)), "error")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True, port=int(os.getenv("PORT", 5000)))
