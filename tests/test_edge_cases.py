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

def _post(title: str, amount: float, category: str, date: str = "2026-08-01") -> dict:
    return client.post(
        "/expenses",
        json={"title": title, "amount": amount, "category": category, "date": date},
    )


# ── Validation: title ─────────────────────────────────────────────────────────

def test_empty_title_returns_422():
    resp = _post(title="", amount=10.0, category="Food")
    assert resp.status_code == 422
    assert "error" in resp.json()


def test_whitespace_only_title_returns_422():
    resp = _post(title="   ", amount=10.0, category="Food")
    assert resp.status_code == 422
    assert "error" in resp.json()


def test_title_exceeding_max_length_returns_422():
    resp = _post(title="x" * 121, amount=10.0, category="Food")
    assert resp.status_code == 422
    assert "error" in resp.json()


# ── Validation: amount ────────────────────────────────────────────────────────

def test_negative_amount_returns_422():
    resp = _post(title="Lunch", amount=-5.0, category="Food")
    assert resp.status_code == 422
    assert "error" in resp.json()


def test_zero_amount_returns_422():
    resp = _post(title="Lunch", amount=0, category="Food")
    assert resp.status_code == 422
    assert "error" in resp.json()


# ── Validation: date ──────────────────────────────────────────────────────────

def test_malformed_date_returns_422_not_500():
    resp = _post(title="Lunch", amount=10.0, category="Food", date="not-a-date")
    assert resp.status_code == 422
    assert "error" in resp.json()


def test_partial_date_returns_422():
    resp = _post(title="Lunch", amount=10.0, category="Food", date="2026-13")
    assert resp.status_code == 422
    assert "error" in resp.json()


# ── Validation: category ──────────────────────────────────────────────────────

def test_empty_category_returns_422():
    resp = _post(title="Lunch", amount=10.0, category="")
    assert resp.status_code == 422
    assert "error" in resp.json()


def test_whitespace_only_category_returns_422():
    resp = _post(title="Lunch", amount=10.0, category="   ")
    assert resp.status_code == 422
    assert "error" in resp.json()


def test_category_preserves_casing_but_strips_whitespace():
    """Category should preserve casing on storage but be stripped of leading/trailing whitespace."""
    resp = _post(title="Lunch", amount=10.0, category="  Food  ")
    assert resp.status_code == 201
    assert resp.json()["category"] == "Food"


# ── Category filtering: case-insensitive ──────────────────────────────────────

def test_filter_category_mixed_case_matches():
    """Querying with 'FOOD' or 'Food' must match expenses stored under 'food'."""
    _post("Lunch", 12.50, "Food")
    for variant in ("Food", "FOOD", "food", "fOoD"):
        resp = client.get("/expenses", params={"category": variant})
        assert resp.status_code == 200
        assert len(resp.json()) == 1, f"Expected 1 result for category='{variant}'"


def test_total_filter_category_mixed_case():
    _post("Lunch", 12.50, "Food")
    for variant in ("Food", "FOOD", "food"):
        resp = client.get("/expenses/total", params={"category": variant})
        assert resp.status_code == 200
        assert resp.json() == {"total": 12.50}


# ── Empty-store safety ────────────────────────────────────────────────────────

def test_list_expenses_empty_store_returns_empty_list():
    resp = client.get("/expenses")
    assert resp.status_code == 200
    assert resp.json() == []


def test_total_empty_store_returns_zero():
    resp = client.get("/expenses/total")
    assert resp.status_code == 200
    assert resp.json() == {"total": 0}


def test_delete_empty_store_returns_404():
    resp = client.delete("/expenses/1")
    assert resp.status_code == 404
    assert "error" in resp.json()


def test_monthly_summary_empty_store_returns_empty_dict():
    resp = client.get("/expenses/summary/monthly")
    assert resp.status_code == 200
    assert resp.json() == {}


# ── Consistent error envelope ─────────────────────────────────────────────────

def test_validation_error_has_error_key():
    """All 422 responses must carry an 'error' key, not FastAPI's default 'detail'."""
    resp = _post(title="", amount=10.0, category="Food")
    assert resp.status_code == 422
    body = resp.json()
    assert "error" in body
    assert "detail" not in body


def test_404_error_has_error_key():
    """404 responses must carry an 'error' key, not FastAPI's default 'detail'."""
    resp = client.delete("/expenses/999")
    assert resp.status_code == 404
    body = resp.json()
    assert "error" in body
    assert "detail" not in body
