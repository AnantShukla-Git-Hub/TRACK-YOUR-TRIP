# Trip Expense Splitter

Split trip expenses fairly among friends.

**Live Demo:** https://anantshukla-git-hub.github.io/TRACK-YOUR-TRIP/

## How Settlement Works

The app uses a greedy algorithm with heaps to minimize transactions:

1. Calculate each person's net balance (paid - owed)
2. Match biggest debtor with biggest creditor
3. Settle as much as possible between them
4. Repeat until everyone is settled

Example: If 4 people need to settle, instead of 6 transactions, you might only need 3.

**Time complexity:** O(n log n) using max heaps

## Tech

FastAPI • React • Railway • GitHub Pages

## Run Locally

Backend:
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Frontend:
```bash
cd frontend-trip
npm install
npm run dev
```

---

Built as a learning project.


## Detailed Explanation of the logic used

# Expense Splitting Logic

## Flow

    EXPENSE
       │
       ▼
    Validate Payments
       │
       ▼
    Calculate Individual Shares
       │
       ▼
    Calculate Net Balances
       │
       ├───────────────┐
       ▼               ▼
    Positive        Negative
    (Receive)         (Pay)
       │               │
       └───────┬───────┘
               ▼
       Match Debtors & Creditors
               │
               ▼
       Final Settlement
               │
               ▼
          Everyone = 0


## 1. Record an Expense

For every expense, the system stores:

- Total expense amount
- Who paid the amount
- Who participated in the expense
- Each participant's share (optional)

Example:

    Total Expense = ₹900

    Anant paid = ₹900

    Participants:
    Anant → ₹300
    Rahul → ₹300
    Amit  → ₹300


## 2. Calculate Individual Shares

The system calculates how much each participant actually owes.

There are two cases:

### Equal Split

If `share_amount_paise = None`, the remaining amount is divided equally among the participants.

### Custom Split

If a participant has an explicit `share_amount_paise`, that amount is used directly.

All money is stored as **integer paise**, not floating-point values.

Example:

    ₹100 ÷ 3

    Member 1 → ₹33.34
    Member 2 → ₹33.33
    Member 3 → ₹33.33

This guarantees that the total always remains exactly ₹100.


## 3. Validate Payments

The total amount paid by all payers must exactly match the expense total.

Example:

    Expense = ₹900

    Anant paid = ₹600
    Rahul paid = ₹300

    Total Paid = ₹900 ✓

If:

    Total Paid ≠ Expense

the expense is rejected with a validation error.


## 4. Calculate Net Balance

After calculating the shares, the system determines each member's net balance.

    Net Balance = Total Paid - Total Share

Meaning:

- **Positive balance** → Member should receive money
- **Negative balance** → Member should pay money
- **Zero balance** → Member is already settled

Example:

    Anant:
    Paid  = ₹900
    Share = ₹300

    Balance = ₹900 - ₹300
            = +₹600


    Rahul:
    Paid  = ₹0
    Share = ₹300

    Balance = ₹0 - ₹300
            = -₹300


    Amit:
    Paid  = ₹0
    Share = ₹300

    Balance = ₹0 - ₹300
            = -₹300

Final balances:

    Anant → +₹600  (receives)
    Rahul → -₹300  (pays)
    Amit  → -₹300  (pays)


## 5. Combine Multiple Expenses

The same calculation is performed for every expense in the trip.

Instead of settling every expense separately, all expenses are combined into one final net balance for each member.

Example:

    Expense 1:
    Anant paid ₹900

    Expense 2:
    Rahul paid ₹600

    After processing all expenses:

    Anant → +₹400
    Rahul → +₹100
    Amit  → -₹500

This means:

    Anant should receive ₹400
    Rahul should receive ₹100
    Amit should pay ₹500


## 6. Final Settlement

Members are divided into two groups:

### Creditors

Members with a positive balance.

    Anant → +₹400
    Rahul → +₹100

They need to **receive money**.

### Debtors

Members with a negative balance.

    Amit → -₹500

They need to **pay money**.

The system matches debtors with creditors and settles as much as possible in each transaction.

Final settlement:

    Amit → Anant ₹400
    Amit → Rahul ₹100

After settlement:

    Anant = ₹0
    Rahul  = ₹0
    Amit   = ₹0

Everyone is settled.


## Core Logic

    PAYMENT
       ↓
    INDIVIDUAL SHARE
       ↓
    NET BALANCE
       ↓
    ┌──────────────────────┐
    │ Positive → RECEIVE   │
    │ Negative → PAY       │
    │ Zero     → SETTLED   │
    └──────────────────────┘
       ↓
    MATCH DEBTORS & CREDITORS
       ↓
    FINAL SETTLEMENT
       ↓
    EVERYONE = 0


## In One Formula

    Net Balance = Total Paid - Total Share


## Overall Idea

The expense splitter converts:

    Multiple Expenses
          ↓
    Individual Shares
          ↓
    Net Balances
          ↓
    Debtors & Creditors
          ↓
    Final Settlement Transactions

The goal is to turn all trip expenses into a small set of transactions that settles everyone's balance exactly.
