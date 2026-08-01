from typing import Optional

from fastapi import FastAPI, Query

from src.models import Expense, ExpenseCreate
from src import storage

app = FastAPI(title="Smart Expense Tracker")


@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/expenses", response_model=Expense, status_code=201)
def create_expense(data: ExpenseCreate) -> Expense:
    """Accept a validated ExpenseCreate payload, persist it, and return the created Expense."""
    return storage.add_expense(data)

@app.get("/expenses", response_model=list[Expense])
def list_expenses(
    category: Optional[str] = Query(default=None, description="Filter by category (case-insensitive)"),
) -> list[Expense]:
    """Return all expenses, optionally filtered by category (case-insensitive)."""
    expenses = storage.get_all_expenses()
    if category is not None:
        expenses = [e for e in expenses if e.category.lower() == category.lower()]
    return expenses
