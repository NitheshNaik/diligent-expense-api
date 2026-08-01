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

def _post(title: str, amount: float, category: str, date: str = "2026-08-01") -> None:
    resp = client.post(
        "/expenses",
        json={"title": title, "amount": amount, "category": category, "date": date},
    )
    assert resp.status_code == 201


# ── tests ─────────────────────────────────────────────────────────────────────

def test_total_no_expenses():
    """Empty store should return 0, not a 404 or error."""
    response = client.get("/expenses/total")
    assert response.status_code == 200
    assert response.json() == {"total": 0}


def test_total_all_expenses():
    _post("Lunch", 12.50, "Food")
    _post("Bus ticket", 2.00, "Transport")
    _post("Coffee", 3.75, "Food")

    response = client.get("/expenses/total")
    assert response.status_code == 200
    assert response.json() == {"total": 18.25}


def test_total_filtered_by_category():
    _post("Lunch", 12.50, "Food")
    _post("Bus ticket", 2.00, "Transport")
    _post("Coffee", 3.75, "Food")

    response = client.get("/expenses/total", params={"category": "Food"})
    assert response.status_code == 200
    assert response.json() == {"total": 16.25}


def test_total_category_no_matches():
    _post("Lunch", 12.50, "Food")

    response = client.get("/expenses/total", params={"category": "Entertainment"})
    assert response.status_code == 200
    assert response.json() == {"total": 0}


def test_total_category_is_case_insensitive():
    _post("Lunch", 12.50, "Food")
    _post("Coffee", 3.75, "food")  # lower-case stored category

    for variant in ("food", "FOOD", "Food"):
        response = client.get("/expenses/total", params={"category": variant})
        assert response.status_code == 200
        assert response.json() == {"total": 16.25}, f"Failed for category='{variant}'"
