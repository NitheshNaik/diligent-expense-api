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


# ── helper ────────────────────────────────────────────────────────────────────

def _post(title: str, amount: float, category: str, date: str) -> None:
    resp = client.post(
        "/expenses",
        json={"title": title, "amount": amount, "category": category, "date": date},
    )
    assert resp.status_code == 201


# ── tests ─────────────────────────────────────────────────────────────────────

def test_monthly_summary_empty_store():
    response = client.get("/expenses/summary/monthly")
    assert response.status_code == 200
    assert response.json() == {}


def test_monthly_summary_single_month():
    _post("Lunch", 12.50, "Food", "2026-08-01")
    _post("Coffee", 3.75, "Food", "2026-08-15")

    response = client.get("/expenses/summary/monthly")
    assert response.status_code == 200
    assert response.json() == {"2026-08": 16.25}


def test_monthly_summary_multiple_months():
    _post("Lunch",      12.50, "Food",      "2026-06-10")
    _post("Bus ticket",  2.00, "Transport", "2026-06-20")
    _post("Dinner",     25.00, "Food",      "2026-07-05")
    _post("Coffee",      3.75, "Food",      "2026-08-01")
    _post("Groceries",  45.00, "Food",      "2026-08-22")

    response = client.get("/expenses/summary/monthly")
    assert response.status_code == 200
    body = response.json()

    assert body == {
        "2026-06": 14.50,
        "2026-07": 25.00,
        "2026-08": 48.75,
    }


def test_monthly_summary_keys_are_sorted_chronologically():
    _post("August item",  10.00, "Food", "2026-08-01")
    _post("June item",    20.00, "Food", "2026-06-01")
    _post("July item",    30.00, "Food", "2026-07-01")

    response = client.get("/expenses/summary/monthly")
    assert response.status_code == 200
    keys = list(response.json().keys())
    assert keys == sorted(keys)


def test_monthly_summary_does_not_include_deleted_expenses():
    _post("Lunch", 12.50, "Food", "2026-08-01")
    resp = client.post(
        "/expenses",
        json={"title": "Coffee", "amount": 3.75, "category": "Food", "date": "2026-08-10"},
    )
    coffee_id = resp.json()["id"]

    client.delete(f"/expenses/{coffee_id}")

    body = client.get("/expenses/summary/monthly").json()
    assert body == {"2026-08": 12.50}
