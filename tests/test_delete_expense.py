import pytest
from fastapi.testclient import TestClient

from src.main import app
from src import storage

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_store():
    """Reset the in-memory store and id counter before each test."""
    storage._store.clear()
    storage._next_id = 1
    yield


# ── helpers ───────────────────────────────────────────────────────────────────

def _post(title: str, amount: float, category: str, date: str = "2026-08-01") -> int:
    """Create an expense and return its assigned id."""
    resp = client.post(
        "/expenses",
        json={"title": title, "amount": amount, "category": category, "date": date},
    )
    assert resp.status_code == 201
    return resp.json()["id"]


# ── tests ─────────────────────────────────────────────────────────────────────

def test_delete_existing_expense_returns_204():
    expense_id = _post("Lunch", 12.50, "Food")
    response = client.delete(f"/expenses/{expense_id}")
    assert response.status_code == 204


def test_delete_nonexistent_id_returns_404():
    response = client.delete("/expenses/999")
    assert response.status_code == 404


def test_deleted_expense_absent_from_list():
    id1 = _post("Lunch", 12.50, "Food")
    id2 = _post("Bus ticket", 2.00, "Transport")

    client.delete(f"/expenses/{id1}")

    response = client.get("/expenses")
    assert response.status_code == 200
    ids_remaining = [e["id"] for e in response.json()]
    assert id1 not in ids_remaining
    assert id2 in ids_remaining


def test_deleted_expense_excluded_from_total():
    _post("Lunch", 12.50, "Food")
    id2 = _post("Coffee", 3.75, "Food")

    # total before deletion
    before = client.get("/expenses/total").json()["total"]
    assert before == 16.25

    client.delete(f"/expenses/{id2}")

    # total after deletion
    after = client.get("/expenses/total").json()["total"]
    assert after == 12.50


def test_double_delete_second_returns_404():
    """Deleting the same id twice: first succeeds, second must 404."""
    expense_id = _post("Dinner", 25.00, "Food")
    assert client.delete(f"/expenses/{expense_id}").status_code == 204
    assert client.delete(f"/expenses/{expense_id}").status_code == 404
