# Trip Expense Splitter

A simple web app to split trip expenses fairly using greedy algorithm for optimal settlement.

## Project Structure (Minimal)

```
TRACK-YOUR-TRIP/
├── index.html           # Complete frontend (HTML + CSS + JavaScript)
├── api/index.py         # Backend for PDF generation only  
├── requirements.txt     # 3 Python dependencies
├── vercel.json         # Deployment configuration
└── README.md           # This file
```

**Total: 5 files only!**

## Algorithm Explained

**Problem:** Split expenses among friends with minimum transactions  
**Solution:** Greedy algorithm with heaps - O(n log n) complexity

### Example Calculation

**Trip: Goa with Anant, Rahul, Amit**

```
Expense 1: Hotel Rs.1200 (Anant paid, split 3 ways = Rs.400 each)
Expense 2: Food Rs.600 (Rahul paid, split 3 ways = Rs.200 each) 
Expense 3: Transport Rs.900 (Amit paid, split 3 ways = Rs.300 each)
```

**Net Balances:**
- Anant: Paid Rs.1200, Owes Rs.900 → Gets Rs.300
- Rahul: Paid Rs.600, Owes Rs.900 → Owes Rs.300  
- Amit: Paid Rs.900, Owes Rs.900 → Settled Rs.0

**Settlement:** Rahul pays Anant Rs.300 (1 transaction instead of 6)

## Features

- Add trip members
- Record expenses (who paid, split among whom)
- Smart settlement calculation (greedy algorithm)
- Professional PDF report generation
- Data saved in browser (localStorage)
- Clean, beginner-friendly code with detailed comments

## Tech Stack

**Frontend:** Vanilla HTML + CSS + JavaScript (no frameworks)  
**Backend:** FastAPI (Python) for PDF generation only  
**Algorithm:** Min/Max heaps for greedy optimization  
**Deployment:** Vercel (serverless)

## Local Development

### Run Frontend:
```bash
# Open index.html in browser
python -m http.server 8080
# Then visit: http://localhost:8080
```

### Run Backend (for PDF):
```bash
pip install -r requirements.txt
uvicorn api.index:app --reload --port 8000
```

## Deployment to Vercel

**Method 1: GitHub**
1. Push code to GitHub
2. Connect repository to Vercel  
3. Auto-deploy!

**Method 2: CLI**
```bash
npm install -g vercel
vercel
```

## Code Structure Explained

### index.html
- **Lines 1-150:** CSS styling (clean, modern design)
- **Lines 151-200:** HTML structure (trip form, members, expenses)  
- **Lines 201-300:** Heap classes (MinHeap, MaxHeap for algorithm)
- **Lines 301-400:** Core functions (add members, expenses, settlement)
- **Lines 401-500:** Settlement algorithm (greedy with heaps)
- **Lines 501-600:** Display update functions
- **Lines 601-700:** PDF generation and utilities

### api/index.py  
- **Lines 1-20:** FastAPI setup with CORS
- **Lines 21-80:** PDF generation function with ReportLab
- **Lines 81-100:** API endpoints and Vercel handler

## Algorithm Details

1. **Calculate Net Balance:** For each person, subtract total owed from total paid
2. **Separate Creditors/Debtors:** Use MaxHeap for creditors, MinHeap for debtors  
3. **Greedy Matching:** Always match biggest creditor with biggest debtor
4. **Minimize Transactions:** Settle maximum amount possible in each transaction

**Time Complexity:** O(n log n) where n = number of members  
**Space Complexity:** O(n) for heaps and balances

## Money Handling

All calculations use floating-point numbers with 2 decimal precision.  
Threshold of Rs.1 used to avoid minor rounding errors.

## Comments Style

Code includes detailed comments explaining:
- **What** each function does
- **Why** specific algorithms are chosen  
- **How** complex logic works step-by-step
- **When** to use different approaches

Perfect for learning data structures and algorithms!

Built as an educational project demonstrating:
- Greedy algorithms
- Heap data structures  
- Full-stack web development
- Clean code practices
