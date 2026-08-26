from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from database import Base


class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    members = relationship("Member", back_populates="trip", cascade="all, delete-orphan")
    expenses = relationship("Expense", back_populates="trip", cascade="all, delete-orphan")


class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)

    trip = relationship("Trip", back_populates="members")


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id", ondelete="CASCADE"), nullable=False)
    description = Column(String, nullable=False)
    total_amount_paise = Column(Integer, nullable=False)

    trip = relationship("Trip", back_populates="expenses")
    payers = relationship("ExpensePayer", back_populates="expense", cascade="all, delete-orphan")
    participants = relationship("ExpenseParticipant", back_populates="expense", cascade="all, delete-orphan")


class ExpensePayer(Base):
    __tablename__ = "expense_payers"

    id = Column(Integer, primary_key=True, index=True)
    expense_id = Column(Integer, ForeignKey("expenses.id", ondelete="CASCADE"), nullable=False)
    member_id = Column(Integer, ForeignKey("members.id", ondelete="CASCADE"), nullable=False)
    amount_paid_paise = Column(Integer, nullable=False)

    expense = relationship("Expense", back_populates="payers")


class ExpenseParticipant(Base):
    __tablename__ = "expense_participants"

    id = Column(Integer, primary_key=True, index=True)
    expense_id = Column(Integer, ForeignKey("expenses.id", ondelete="CASCADE"), nullable=False)
    member_id = Column(Integer, ForeignKey("members.id", ondelete="CASCADE"), nullable=False)
    share_amount_paise = Column(Integer, nullable=True)  # null = equal split

    expense = relationship("Expense", back_populates="participants")