from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.models import Expense, ExpenseCreate
from src import storage

app = FastAPI(
    title="Smart Expense Tracker API",
    description=(
        "A lightweight REST API to track, query, summarize, and manage personal expenses. "
        "Uses an in-memory backend."
    ),
    version="1.0.0",
)


# ── Consistent error envelope ─────────────────────────────────────────────────

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Return all Pydantic validation errors as {"error": "<message>"}."""
    messages = "; ".join(
        f"{' -> '.join(str(loc) for loc in err['loc'])}: {err['msg']}"
        for err in exc.errors()
    )
    return JSONResponse(status_code=422, content={"error": messages})


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Return HTTPException details as {"error": "<message>"}."""
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get(
    "/health",
    summary="Check API Health",
)
def health_check():
    """Return the operational health status of the application."""
    return {"status": "ok"}


@app.post(
    "/expenses",
    response_model=Expense,
    status_code=201,
    summary="Create a New Expense",
)
def create_expense(data: ExpenseCreate) -> Expense:
    """Validate and persist a new expense payload. The server assigns a unique ID."""
    return storage.add_expense(data)


@app.get(
    "/expenses/summary/monthly",
    summary="Get Monthly Expense Summary",
)
def monthly_summary() -> dict[str, float]:
    """Calculate and return total expense amounts grouped chronologically by calendar month (YYYY-MM)."""
    expenses = storage.get_all_expenses()
    totals: dict[str, float] = {}
    for expense in expenses:
        key = expense.date.strftime("%Y-%m")
        totals[key] = round(totals.get(key, 0.0) + expense.amount, 2)
    return dict(sorted(totals.items()))


@app.get(
    "/expenses/total",
    summary="Get Total Sum of Expenses",
)
def get_total(
    category: Optional[str] = Query(
        default=None,
        description="Filter total calculation by specific category (case-insensitive)",
    ),
) -> dict:
    """Calculate the sum of all expenses, with an optional filter for a specific category."""
    expenses = storage.filter_expenses(category)
    return {"total": round(sum(e.amount for e in expenses), 2)}


@app.get(
    "/expenses",
    response_model=list[Expense],
    summary="List and Filter Expenses",
)
def list_expenses(
    category: Optional[str] = Query(
        default=None,
        description="Filter listing by specific category (case-insensitive)",
    ),
) -> list[Expense]:
    """Return a list of all expenses, with an optional filter for a specific category."""
    return storage.filter_expenses(category)


@app.delete(
    "/expenses/{expense_id}",
    status_code=204,
    summary="Delete an Expense by ID",
)
def delete_expense(expense_id: int) -> Response:
    """Delete a recorded expense by its unique ID. Returns 204 on success, or 404 if not found."""
    deleted = storage.delete_expense(expense_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Expense {expense_id} not found")
    return Response(status_code=204)
