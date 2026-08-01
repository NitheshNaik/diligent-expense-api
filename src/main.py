from fastapi import FastAPI

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
