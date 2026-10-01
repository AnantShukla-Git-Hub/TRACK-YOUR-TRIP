from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field




class TripCreate(BaseModel):
    name: str = Field(min_length=1)


class TripOut(BaseModel):
    id: int
    name: str
    created_at: datetime

    class Config:
        from_attributes = True




class MemberCreate(BaseModel):
    name: str = Field(min_length=1)


class MemberOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True




class ExpensePayerIn(BaseModel):
    member_id: int
    amount_paid_paise: int = Field(gt=0)


class ExpenseParticipantIn(BaseModel):
    member_id: int
    share_amount_paise: Optional[int] = Field(default=None, ge=0)


class ExpenseCreate(BaseModel):
    description: str = Field(min_length=1)
    total_amount_paise: int = Field(gt=0)
    payers: List[ExpensePayerIn] = Field(min_length=1)
    participants: List[ExpenseParticipantIn] = Field(min_length=1)


class ExpensePayerOut(BaseModel):
    member_id: int
    amount_paid_paise: int

    class Config:
        from_attributes = True


class ExpenseParticipantOut(BaseModel):
    member_id: int
    share_amount_paise: Optional[int]

    class Config:
        from_attributes = True


class ExpenseOut(BaseModel):
    id: int
    description: str
    total_amount_paise: int
    payers: List[ExpensePayerOut]
    participants: List[ExpenseParticipantOut]

    class Config:
        from_attributes = True




class MemberBalance(BaseModel):
    member_id: int
    member_name: str
    net_balance_paise: int


class SettlementTransaction(BaseModel):
    debtor_id: int
    debtor_name: str
    creditor_id: int
    creditor_name: str
    amount_paise: int


class SettlementOut(BaseModel):
    grand_total_paise: int
    balances: List[MemberBalance]
    transactions: List[SettlementTransaction]




class ExpenseShareLine(BaseModel):
    member_id: int
    member_name: str
    share_paise: int


class ExpensePayerLine(BaseModel):
    member_id: int
    member_name: str
    amount_paid_paise: int


class ExpenseSheetLine(BaseModel):
    expense_id: int
    description: str
    total_amount_paise: int
    payers: List[ExpensePayerLine]
    shares: List[ExpenseShareLine]


class TripSheet(BaseModel):
    trip_id: int
    trip_name: str
    generated_at: datetime
    expenses: List[ExpenseSheetLine]
    balances: List[MemberBalance]
    transactions: List[SettlementTransaction]