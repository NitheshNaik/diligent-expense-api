from datetime import date
from pydantic import BaseModel, field_validator

# Maximum length for freeform text fields
_TITLE_MAX_LEN = 120
_CATEGORY_MAX_LEN = 60


class ExpenseCreate(BaseModel):
    """Input model for creating an expense. The server assigns the id."""

    title: str
    amount: float
    category: str
    date: date

    @field_validator("title")
    @classmethod
    def title_must_be_non_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("title must not be empty or whitespace")
        if len(v) > _TITLE_MAX_LEN:
            raise ValueError(f"title must not exceed {_TITLE_MAX_LEN} characters")
        return v

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("amount must be greater than 0")
        return v

    @field_validator("category")
    @classmethod
    def category_must_be_non_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("category must not be empty or whitespace")
        if len(v) > _CATEGORY_MAX_LEN:
            raise ValueError(f"category must not exceed {_CATEGORY_MAX_LEN} characters")
        return v

    # `date` is declared as Python's `datetime.date`, so Pydantic already
    # rejects non-ISO strings with a ValidationError (→ 422). No extra
    # validator is needed; the type annotation does the work.


class Expense(ExpenseCreate):
    """Full expense model including server-assigned id."""

    id: int
