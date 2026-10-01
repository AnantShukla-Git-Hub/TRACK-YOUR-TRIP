# Trip Expense Splitter

A simple web app to split trip expenses fairly using greedy algorithm for optimal settlement.

## Tech Stack

**Frontend:** Vanilla HTML + CSS + JavaScript
**Backend:** FastAPI (Python) for PDF generation only  
**Algorithm:** Min/Max heaps for greedy algorithm  
**Deployment:** Vercel 

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

Built as an educational project demonstrating:
- Greedy algorithms
- Heap data structures  
- Full-stack web development
- Clean code practices
