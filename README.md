# Trip Expense Splitter

Split trip expenses fairly among friends with optimal settlement using greedy algorithm.

## Features

- Create trips and add members
- Track expenses with multiple payers
- Smart settlement with minimal transactions
- Download PDF settlement report
- Data stored locally in browser
- Fast and simple

## Algorithm

Uses greedy algorithm with max/min heaps for optimal settlement.
Time complexity: O(n log n)

Example: 4 people settling needs only 3 transactions instead of 6.

### Settlement Calculation Example

**Trip: Goa 2024 with 3 friends**

**Expenses:**
```
Expense 1: Hotel Rs.1200
- Anant paid Rs.1200
- Split among: Anant, Rahul, Amit (Rs.400 each)

Expense 2: Food Rs.600  
- Rahul paid Rs.600
- Split among: Anant, Rahul, Amit (Rs.200 each)

Expense 3: Transport Rs.900
- Amit paid Rs.900  
- Split among: Anant, Rahul, Amit (Rs.300 each)
```

**Step 1: Calculate what each person paid vs owes**
```
Anant: Paid Rs.1200, Owes Rs.900 (400+200+300) → Net: +Rs.300
Rahul: Paid Rs.600, Owes Rs.900 (400+200+300)  → Net: -Rs.300  
Amit:  Paid Rs.900, Owes Rs.900 (400+200+300)  → Net: Rs.0
```

**Step 2: Greedy settlement (match largest creditor with largest debtor)**
```
Creditors: Anant (+Rs.300)
Debtors:   Rahul (-Rs.300)
Settled:   Amit (Rs.0)

Final settlement: Rahul pays Anant Rs.300
```

**Result: 1 transaction settles everything instead of 6 individual payments**

**Without algorithm:** 6 transactions needed
**With algorithm:** 1 transaction needed

This scales to larger groups - 10 people might need only 4-5 transactions instead of 45.

## Tech Stack

Frontend: React + Vite  
Backend: FastAPI (Python)  
Storage: localStorage  
PDF: ReportLab  
Deployment: Vercel

## Local Development

### Frontend:
```bash
cd frontend-trip
npm install
npm run dev
```

### Backend (for PDF):
```bash
pip install -r requirements.txt
uvicorn api.index:app --reload
```

## Deploy to Vercel

```bash
git push origin main
```

Vercel auto-deploys from GitHub.

Or use Vercel CLI:
```bash
vercel
```

## Project Structure

```
TRACK-YOUR-TRIP/
├── api/
│   └── index.py          # PDF generation endpoint
├── frontend-trip/
│   ├── src/
│   │   ├── components/   # React components
│   │   └── services/     # Storage & settlement logic
│   └── package.json
├── requirements.txt      # Python dependencies
└── vercel.json          # Deployment config
```

## How It Works

1. Enter trip details and members
2. Add expenses (who paid, who participated)
3. Algorithm calculates net balances
4. Minimizes settlement transactions
5. Download professional PDF report

All calculations use integer arithmetic (paise) to avoid decimal errors.

Built as a learning project.
