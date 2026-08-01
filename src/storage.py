from src.models import Expense, ExpenseCreate

# In-memory store: maps id (int) -> Expense
_store: dict[int, Expense] = {}
_next_id: int = 1


def add_expense(data: ExpenseCreate) -> Expense:
    """Create a new Expense from data, assign an auto-incremented id, and persist it."""
    global _next_id
    expense = Expense(id=_next_id, **data.model_dump())
    _store[_next_id] = expense
    _next_id += 1
    return expense


def get_all_expenses() -> list[Expense]:
    """Return all stored expenses."""
    return list(_store.values())


def get_expense_by_id(expense_id: int) -> Expense | None:
    """Return the expense with the given id, or None if not found."""
    return _store.get(expense_id)


def delete_expense(expense_id: int) -> bool:
    """Delete the expense with the given id. Returns True if deleted, False if not found."""
    if expense_id in _store:
        del _store[expense_id]
        return True
    return False
