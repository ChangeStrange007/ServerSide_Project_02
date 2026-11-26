"""CRUD tests for the League of Legends Items API.

Every test checks the HTTP status code AND the data in the response body.
Where it matters, a follow-up GET confirms the change really persisted.
"""


# ---------------------------------------------------------------- CREATE (POST)
class TestCreate:
    def test_create_item_returns_201_and_saves_correct_data(self, client, infinity_edge):
        resp = client.post("/items", json=infinity_edge)

        assert resp.status_code == 201
        data = resp.json()
        assert isinstance(data["id"], int)
        for field, value in infinity_edge.items():
            assert data[field] == value, f"{field} was not saved correctly"
        assert data["created_at"] and data["updated_at"]

        # It really persisted, and not just echoed back.
        fetched = client.get(f"/items/{data['id']}")
        assert fetched.status_code == 200
        assert fetched.json() == data

    def test_create_applies_defaults_for_omitted_fields(self, client, rabadons):
        data = client.post("/items", json=rabadons).json()

        assert data["ability_power"] == 140
        assert data["attack_damage"] == 0
        assert data["armor"] == 0
        assert data["crit_chance"] == 0
        assert data["description"] is None
        assert data["is_purchasable"] is True

    def test_create_rejects_duplicate_name_with_409(self, client, infinity_edge):
        client.post("/items", json=infinity_edge)
        resp = client.post("/items", json=infinity_edge)

        assert resp.status_code == 409
        assert "already exists" in resp.json()["detail"]
        assert len(client.get("/items").json()) == 1  # no second record created

    def test_create_rejects_invalid_data_with_422(self, client, infinity_edge):
        bad_cost = client.post("/items", json={**infinity_edge, "gold_cost": -1})
        bad_category = client.post("/items", json={**infinity_edge, "name": "X", "category": "not-a-category"})
        missing_name = client.post("/items", json={"category": "boots", "gold_cost": 100})

        for resp in (bad_cost, bad_category, missing_name):
            assert resp.status_code == 422
        assert bad_cost.json()["detail"][0]["loc"][-1] == "gold_cost"
        assert bad_category.json()["detail"][0]["loc"][-1] == "category"
        assert missing_name.json()["detail"][0]["loc"][-1] == "name"
        assert client.get("/items").json() == []  # nothing was saved


# ------------------------------------------------------------- READ ALL (GET)
class TestReadAll:
    def test_read_all_returns_empty_list_when_no_items(self, client):
        resp = client.get("/items")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_read_all_returns_every_record_with_correct_data(self, client, infinity_edge, rabadons, boots):
        created = [client.post("/items", json=p).json() for p in (infinity_edge, rabadons, boots)]

        resp = client.get("/items")

        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 3
        assert data == created  # same records, in id order
        assert [i["name"] for i in data] == ["Infinity Edge", "Rabadon's Deathcap", "Boots of Swiftness"]

    def test_read_all_filters_by_category_and_search(self, client, infinity_edge, rabadons, boots):
        for p in (infinity_edge, rabadons, boots):
            client.post("/items", json=p)

        legendary = client.get("/items", params={"category": "legendary"})
        searched = client.get("/items", params={"search": "boots"})

        assert legendary.status_code == 200
        assert {i["name"] for i in legendary.json()} == {"Infinity Edge", "Rabadon's Deathcap"}
        assert [i["name"] for i in searched.json()] == ["Boots of Swiftness"]

    def test_read_all_pagination(self, client, infinity_edge, rabadons, boots):
        for p in (infinity_edge, rabadons, boots):
            client.post("/items", json=p)

        page = client.get("/items", params={"skip": 1, "limit": 1})

        assert page.status_code == 200
        assert [i["name"] for i in page.json()] == ["Rabadon's Deathcap"]


# -------------------------------------------------------------- READ ONE (GET)
class TestReadOne:
    def test_read_one_returns_the_requested_item(self, client, infinity_edge, rabadons):
        client.post("/items", json=infinity_edge)
        second = client.post("/items", json=rabadons).json()

        resp = client.get(f"/items/{second['id']}")

        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == second["id"]
        assert data["name"] == "Rabadon's Deathcap"
        assert data["ability_power"] == 140
        assert data["gold_cost"] == 3600

    def test_read_one_unknown_id_returns_404(self, client):
        resp = client.get("/items/9999")
        assert resp.status_code == 404
        assert "9999" in resp.json()["detail"]

    def test_read_one_non_integer_id_returns_422(self, client):
        assert client.get("/items/abc").status_code == 422


# ---------------------------------------------------------------- UPDATE (PUT)
class TestUpdatePut:
    def test_put_replaces_the_whole_record(self, client, infinity_edge):
        item_id = client.post("/items", json=infinity_edge).json()["id"]
        replacement = {
            "name": "Infinity Edge",
            "category": "legendary",
            "gold_cost": 3500,  # changed
            "attack_damage": 75,  # changed
            # crit_chance, description, passive omitted -> reset to defaults
        }

        resp = client.put(f"/items/{item_id}", json=replacement)

        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == item_id
        assert data["gold_cost"] == 3500
        assert data["attack_damage"] == 75
        assert data["crit_chance"] == 0
        assert data["description"] is None
        assert data["passive"] is None

        assert client.get(f"/items/{item_id}").json() == data  # persisted

    def test_put_unknown_id_returns_404(self, client, infinity_edge):
        assert client.put("/items/9999", json=infinity_edge).status_code == 404

    def test_put_to_existing_name_returns_409_and_leaves_data_unchanged(self, client, infinity_edge, rabadons):
        client.post("/items", json=infinity_edge)
        other_id = client.post("/items", json=rabadons).json()["id"]

        resp = client.put(f"/items/{other_id}", json={**rabadons, "name": "Infinity Edge"})

        assert resp.status_code == 409
        assert client.get(f"/items/{other_id}").json()["name"] == "Rabadon's Deathcap"

    def test_put_invalid_data_returns_422(self, client, infinity_edge):
        item_id = client.post("/items", json=infinity_edge).json()["id"]
        resp = client.put(f"/items/{item_id}", json={**infinity_edge, "crit_chance": 150})
        assert resp.status_code == 422
        assert client.get(f"/items/{item_id}").json()["crit_chance"] == 25  # unchanged


# -------------------------------------------------------------- UPDATE (PATCH)
class TestUpdatePatch:
    def test_patch_changes_only_the_sent_fields(self, client, infinity_edge):
        created = client.post("/items", json=infinity_edge).json()

        resp = client.patch(f"/items/{created['id']}", json={"gold_cost": 3200, "armor": 10})

        assert resp.status_code == 200
        data = resp.json()
        assert data["gold_cost"] == 3200
        assert data["armor"] == 10
        # everything else untouched
        assert data["name"] == created["name"]
        assert data["attack_damage"] == created["attack_damage"]
        assert data["crit_chance"] == created["crit_chance"]
        assert data["passive"] == created["passive"]

        assert client.get(f"/items/{created['id']}").json() == data  # persisted

    def test_patch_can_clear_optional_field(self, client, infinity_edge):
        item_id = client.post("/items", json=infinity_edge).json()["id"]
        data = client.patch(f"/items/{item_id}", json={"passive": None}).json()
        assert data["passive"] is None
        assert data["name"] == "Infinity Edge"

    def test_patch_rejects_null_for_required_field(self, client, infinity_edge):
        item_id = client.post("/items", json=infinity_edge).json()["id"]
        resp = client.patch(f"/items/{item_id}", json={"name": None})
        assert resp.status_code == 422
        assert client.get(f"/items/{item_id}").json()["name"] == "Infinity Edge"

    def test_patch_unknown_id_returns_404(self, client):
        assert client.patch("/items/9999", json={"gold_cost": 1}).status_code == 404


# ------------------------------------------------------------- DELETE (DELETE)
class TestDelete:
    def test_delete_removes_the_record(self, client, infinity_edge):
        item_id = client.post("/items", json=infinity_edge).json()["id"]

        resp = client.delete(f"/items/{item_id}")

        assert resp.status_code == 204
        assert resp.content == b""
        assert client.get(f"/items/{item_id}").status_code == 404
        assert client.get("/items").json() == []

    def test_delete_only_removes_the_targeted_item(self, client, infinity_edge, rabadons):
        first = client.post("/items", json=infinity_edge).json()
        second = client.post("/items", json=rabadons).json()

        assert client.delete(f"/items/{first['id']}").status_code == 204

        remaining = client.get("/items").json()
        assert remaining == [second]

    def test_delete_unknown_id_returns_404(self, client):
        assert client.delete("/items/9999").status_code == 404

    def test_delete_twice_second_call_returns_404(self, client, infinity_edge):
        item_id = client.post("/items", json=infinity_edge).json()["id"]
        assert client.delete(f"/items/{item_id}").status_code == 204
        assert client.delete(f"/items/{item_id}").status_code == 404
