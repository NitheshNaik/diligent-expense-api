import pytest
from fastapi.testclient import TestClient

from src.main import app
from src import storage


@pytest.fixture(autouse=True)
def reset_store():
    """Reset the in-memory store and id counter before each test."""
    storage._store.clear()
    storage._next_id = 1
    yield


client = TestClient(app)

VALID_PAYLOAD = {
    "title": "Lunch",
    "amount": 12.50,
    "category": "Food",
    "date": "2026-08-01",
}


def test_create_expense_success():
    response = client.post("/expenses", json=VALID_PAYLOAD)
    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert body["title"] == "Lunch"
    assert body["amount"] == 12.50
    assert body["category"] == "Food"
    assert body["date"] == "2026-08-01"


def test_create_expense_negative_amount_returns_422():
    payload = {**VALID_PAYLOAD, "amount": -5.0}
    response = client.post("/expenses", json=payload)
    assert response.status_code == 422


def test_create_expense_zero_amount_returns_422():
    payload = {**VALID_PAYLOAD, "amount": 0}
    response = client.post("/expenses", json=payload)
    assert response.status_code == 422
