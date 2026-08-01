from datetime import date
from pydantic import BaseModel, field_validator


class ExpenseCreate(BaseModel):
    """Input model for creating an expense. The server assigns the id."""

    title: str
    amount: float
    category: str
    date: date

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("amount must be greater than 0")
        return v


class Expense(ExpenseCreate):
    """Full expense model including server-assigned id."""

    id: int
