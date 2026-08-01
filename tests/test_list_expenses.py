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


# ── helpers ──────────────────────────────────────────────────────────────────

def _post(title: str, amount: float, category: str, date: str = "2026-08-01") -> dict:
    resp = client.post(
        "/expenses",
        json={"title": title, "amount": amount, "category": category, "date": date},
    )
    assert resp.status_code == 201
    return resp.json()


# ── tests ─────────────────────────────────────────────────────────────────────

def test_list_expenses_empty():
    response = client.get("/expenses")
    assert response.status_code == 200
    assert response.json() == []


def test_list_expenses_multiple():
    _post("Lunch", 12.50, "Food")
    _post("Bus ticket", 2.00, "Transport")
    _post("Coffee", 3.75, "Food")

    response = client.get("/expenses")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 3
    assert [e["id"] for e in body] == [1, 2, 3]


def test_filter_by_category_no_matches():
    _post("Lunch", 12.50, "Food")

    response = client.get("/expenses", params={"category": "Entertainment"})
    assert response.status_code == 200
    assert response.json() == []


def test_filter_by_category_one_match():
    _post("Bus ticket", 2.00, "Transport")
    _post("Lunch", 12.50, "Food")

    response = client.get("/expenses", params={"category": "Transport"})
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["category"] == "Transport"
    assert body[0]["title"] == "Bus ticket"


def test_filter_by_category_many_matches():
    _post("Lunch", 12.50, "Food")
    _post("Coffee", 3.75, "Food")
    _post("Bus ticket", 2.00, "Transport")
    _post("Dinner", 25.00, "Food")

    response = client.get("/expenses", params={"category": "Food"})
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 3
    assert all(e["category"] == "Food" for e in body)


def test_filter_category_is_case_insensitive():
    _post("Lunch", 12.50, "Food")

    for variant in ("food", "FOOD", "fOoD"):
        response = client.get("/expenses", params={"category": variant})
        assert response.status_code == 200
        assert len(response.json()) == 1, f"Expected 1 result for category='{variant}'"
