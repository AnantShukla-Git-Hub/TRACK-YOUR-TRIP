# Trip Expense Splitter

A clean web app to track and split group expenses fairly.

## Features

- Track trip expenses with multiple payers
- Smart equal/custom split
- Settlement calculation (minimized transactions)
- PDF export
- Mobile responsive

## Tech Stack

**Backend:** FastAPI, SQLAlchemy, SQLite  
**Frontend:** React, Vite, Vanilla CSS

## Local Setup

### Backend
```bash
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend-trip
npm install
npm run dev
```

## Deployment

- **Backend:** Deploy on Render/Railway (free tier)
- **Frontend:** Deploy on Vercel/Netlify (free tier)

## License

MIT
