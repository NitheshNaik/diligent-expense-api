from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Response

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

@app.get("/expenses/total")
def get_total(
    category: Optional[str] = Query(default=None, description="Filter by category (case-insensitive)"),
) -> dict:
    """Return the sum of expense amounts, optionally filtered by category."""
    expenses = storage.filter_expenses(category)
    return {"total": round(sum(e.amount for e in expenses), 2)}


@app.get("/expenses", response_model=list[Expense])
def list_expenses(
    category: Optional[str] = Query(default=None, description="Filter by category (case-insensitive)"),
) -> list[Expense]:
    """Return all expenses, optionally filtered by category (case-insensitive)."""
    return storage.filter_expenses(category)


@app.delete("/expenses/{expense_id}", status_code=204)
def delete_expense(expense_id: int) -> Response:
    """Delete the expense with the given id. Returns 204 on success, 404 if not found."""
    deleted = storage.delete_expense(expense_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Expense {expense_id} not found")
    return Response(status_code=204)
