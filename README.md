# Trip Expense Splitter

Split trip expenses fairly among friends.

Deployed on Vercel - Full-stack serverless application

## How Settlement Works

The app uses a greedy algorithm with heaps to minimize transactions:

1. Calculate each person's net balance (paid - owed)
2. Match biggest debtor with biggest creditor
3. Settle as much as possible between them
4. Repeat until everyone is settled

Example: If 4 people need to settle, instead of 6 transactions, you might only need 3.

Time complexity: O(n log n) using max heaps

## Tech Stack

**Frontend:** React 19 + Vite + Tailwind CSS  
**Backend:** FastAPI (Python)  
**Storage:** In-memory with JSON file persistence  
**Deployment:** Vercel (serverless functions + static hosting)  
**PDF Generation:** ReportLab

## Architecture

- No Database: Uses in-memory storage with JSON file backup at /tmp/trip_data.json
- Serverless: Backend runs as Vercel serverless functions
- Unified Deployment: Frontend and backend deployed together on Vercel

## Deploy to Vercel

### One-Click Deploy

Deploy with Vercel: https://vercel.com/new/clone?repository-url=https://github.com/YOUR_USERNAME/TRACK-YOUR-TRIP

### Manual Deployment

1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Login to Vercel:
```bash
vercel login
```

3. Deploy:
```bash
cd TRACK-YOUR-TRIP
vercel
```

4. Follow the prompts:
   - Link to existing project or create new
   - Accept default settings
   - Deploy

### Configuration

The project is pre-configured with vercel.json:
- Frontend built from frontend-trip/
- Backend API at /api/*
- Python 3.11 runtime
- No environment variables needed

## Run Locally

### Backend:
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Backend runs at http://localhost:8000

### Frontend:
```bash
cd frontend-trip
npm install
npm run dev
```

Frontend runs at http://localhost:5173

## Project Structure

```
TRACK-YOUR-TRIP/
├── api/
│   └── index.py          # Vercel serverless entry point
├── frontend-trip/        # React frontend
│   ├── src/
│   ├── public/
│   └── package.json
├── main.py              # FastAPI application
├── storage.py           # In-memory + JSON storage
├── settlement.py        # Settlement algorithm
├── schemas.py           # Pydantic models
├── models.py            # Data model documentation
├── requirements.txt     # Python dependencies
└── vercel.json         # Vercel configuration
```

## Features

- Create trips and add members
- Track expenses with multiple payers
- Split bills equally or with custom amounts
- Smart settlement with minimal transactions
- Download PDF settlement report
- In-memory storage (fast & simple)
- Serverless deployment (no server maintenance)

## Important Notes

**Data Persistence:** Data is stored in /tmp/trip_data.json which persists during the serverless function's lifecycle

**Ephemeral Storage:** On Vercel, serverless functions are stateless. Data may be lost between deployments or cold starts

**Recommendation:** Always download the PDF report to keep a permanent record

**Best For:** Short-term trip expense tracking, not long-term storage

## Detailed Explanation of the Logic Used

### Expense Splitting Flow

```
    EXPENSE
       |
       v
    Validate Payments
       |
       v
    Calculate Individual Shares
       |
       v
    Calculate Net Balances
       |
       +---------------+
       v               v
    Positive        Negative
    (Receive)         (Pay)
       |               |
       +-------+-------+
               v
       Match Debtors & Creditors
               |
               v
       Final Settlement
               |
               v
          Everyone = 0
```

### 1. Record an Expense

For every expense, the system stores:
- Total expense amount
- Who paid the amount
- Who participated in the expense
- Each participant's share (optional)

### 2. Calculate Individual Shares

The system calculates how much each participant actually owes.

Equal Split: If share_amount_paise = None, the remaining amount is divided equally among participants.

Custom Split: If a participant has an explicit share_amount_paise, that amount is used directly.

All money is stored as integer paise (1 rupee = 100 paise), avoiding floating-point errors.

### 3. Validate Payments

The total amount paid by all payers must exactly match the expense total.

```
Expense = Rs.900
Anant paid = Rs.600
Rahul paid = Rs.300
Total Paid = Rs.900 (valid)
```

### 4. Calculate Net Balance

```
Net Balance = Total Paid - Total Share
```

- Positive balance: Member should receive money
- Negative balance: Member should pay money
- Zero balance: Member is already settled

### 5. Combine Multiple Expenses

All expenses are combined into one final net balance for each member, then settled with minimal transactions.

### 6. Final Settlement

The system matches debtors with creditors using a greedy algorithm with max-heaps for optimal transaction minimization.

Built as a learning project for full-stack serverless development.
