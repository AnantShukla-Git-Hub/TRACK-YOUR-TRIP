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
