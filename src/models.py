import datetime
from pydantic import BaseModel, Field, field_validator

# Maximum length for freeform text fields
_TITLE_MAX_LEN = 120
_CATEGORY_MAX_LEN = 60


class ExpenseCreate(BaseModel):
    """Input model for creating an expense. The server assigns the id."""

    title: str = Field(
        ...,
        description="Short summary or name of the expense (e.g., merchant name, item description)",
        examples=["Lunch at Joe's Cafe", "Monthly cloud hosting"],
        max_length=_TITLE_MAX_LEN,
    )
    amount: float = Field(
        ...,
        description="The positive dollar value of the expense",
        examples=[12.50, 2450.00],
    )
    category: str = Field(
        ...,
        description="Category label to organize and filter expenses (case-insensitive)",
        examples=["Food", "Infrastructure", "Travel"],
        max_length=_CATEGORY_MAX_LEN,
    )
    date: datetime.date = Field(
        ...,
        description="The calendar date of the expense in ISO-8601 format (YYYY-MM-DD)",
        examples=["2026-08-01"],
    )

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


class Expense(ExpenseCreate):
    """Full expense model including server-assigned id."""

    id: int = Field(
        ...,
        description="Unique auto-incrementing integer identifier assigned by the server",
        examples=[1, 42],
    )
