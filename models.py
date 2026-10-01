from datetime import datetime
from typing import Optional


class Trip:
    id: int
    name: str
    created_at: str
    

class Member:
    id: int
    trip_id: int
    name: str


class Expense:
    id: int
    trip_id: int
    description: str
    total_amount_paise: int
    payers: list
    participants: list


class ExpensePayer:
    id: int
    expense_id: int
    member_id: int
    amount_paid_paise: int


class ExpenseParticipant:
    id: int
    expense_id: int
    member_id: int
    share_amount_paise: Optional[int]