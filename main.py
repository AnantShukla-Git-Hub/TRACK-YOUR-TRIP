"""
FastAPI application for the trip expense splitter.
"""
from io import BytesIO
from zoneinfo import ZoneInfo
from fastapi.responses import StreamingResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import Expense, ExpenseParticipant, ExpensePayer, Member, Trip
import schemas
import settlement

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Trip Expense Splitter")

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_trip_or_404(trip_id: int, db: Session) -> Trip:
    trip = db.get(Trip, trip_id)
    if trip is None:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip


def get_member_ids_for_trip(trip_id: int, db: Session) -> set[int]:
    rows = db.query(Member.id).filter(Member.trip_id == trip_id).all()
    return {row[0] for row in rows}


# ---- Trip ----

@app.post("/trips", response_model=schemas.TripOut)
def create_trip(payload: schemas.TripCreate, db: Session = Depends(get_db)):
    trip = Trip(name=payload.name)
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return trip


@app.get("/trips/{trip_id}", response_model=schemas.TripOut)
def get_trip(trip_id: int, db: Session = Depends(get_db)):
    return get_trip_or_404(trip_id, db)


# ---- Members ----

@app.post("/trips/{trip_id}/members", response_model=schemas.MemberOut)
def add_member(trip_id: int, payload: schemas.MemberCreate, db: Session = Depends(get_db)):
    get_trip_or_404(trip_id, db)
    member = Member(trip_id=trip_id, name=payload.name)
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


@app.get("/trips/{trip_id}/members", response_model=list[schemas.MemberOut])
def list_members(trip_id: int, db: Session = Depends(get_db)):
    get_trip_or_404(trip_id, db)
    return db.query(Member).filter(Member.trip_id == trip_id).all()


def is_member_used(member_id: int, db: Session) -> bool:
    payer_exists = db.query(ExpensePayer).filter(ExpensePayer.member_id == member_id).first()
    participant_exists = (
        db.query(ExpenseParticipant).filter(ExpenseParticipant.member_id == member_id).first()
    )
    return payer_exists is not None or participant_exists is not None


@app.delete("/trips/{trip_id}/members/{member_id}", status_code=204)
def delete_member(trip_id: int, member_id: int, db: Session = Depends(get_db)):
    get_trip_or_404(trip_id, db)
    member = (
        db.query(Member)
        .filter(Member.trip_id == trip_id, Member.id == member_id)
        .first()
    )
    if member is None:
        raise HTTPException(status_code=404, detail="Member not found")

    if is_member_used(member_id, db):
        raise HTTPException(
            status_code=400,
            detail="This member is already part of an expense; cannot delete without affecting past records.",
        )

    db.delete(member)
    db.commit()
    return None


# ---- Expenses ----

@app.post("/trips/{trip_id}/expenses", response_model=schemas.ExpenseOut)
def add_expense(trip_id: int, payload: schemas.ExpenseCreate, db: Session = Depends(get_db)):
    get_trip_or_404(trip_id, db)
    valid_member_ids = get_member_ids_for_trip(trip_id, db)

    payer_ids = {p.member_id for p in payload.payers}
    participant_ids = {p.member_id for p in payload.participants}

    unknown_ids = (payer_ids | participant_ids) - valid_member_ids
    if unknown_ids:
        raise HTTPException(
            status_code=400,
            detail=f"Member ids not part of this trip: {sorted(unknown_ids)}",
        )

    payers_data = [
        {"member_id": p.member_id, "amount_paid_paise": p.amount_paid_paise}
        for p in payload.payers
    ]
    participants_data = [
        {"member_id": p.member_id, "share_amount_paise": p.share_amount_paise}
        for p in payload.participants
    ]

    try:
        settlement.validate_payers(payload.total_amount_paise, payers_data)
        settlement.compute_expense_shares(payload.total_amount_paise, participants_data)
    except (settlement.PayerValidationError, settlement.ShareValidationError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    expense = Expense(
        trip_id=trip_id,
        description=payload.description,
        total_amount_paise=payload.total_amount_paise,
    )
    expense.payers = [
        ExpensePayer(member_id=p.member_id, amount_paid_paise=p.amount_paid_paise)
        for p in payload.payers
    ]
    expense.participants = [
        ExpenseParticipant(member_id=p.member_id, share_amount_paise=p.share_amount_paise)
        for p in payload.participants
    ]

    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


@app.get("/trips/{trip_id}/expenses", response_model=list[schemas.ExpenseOut])
def list_expenses(trip_id: int, db: Session = Depends(get_db)):
    get_trip_or_404(trip_id, db)
    return db.query(Expense).filter(Expense.trip_id == trip_id).all()


# ---- Settlement ----

def _build_expense_dicts(trip_id: int, db: Session) -> list[dict]:
    expenses = db.query(Expense).filter(Expense.trip_id == trip_id).all()
    result = []
    for expense in expenses:
        result.append(
            {
                "total_amount_paise": expense.total_amount_paise,
                "payers": [
                    {"member_id": p.member_id, "amount_paid_paise": p.amount_paid_paise}
                    for p in expense.payers
                ],
                "participants": [
                    {"member_id": p.member_id, "share_amount_paise": p.share_amount_paise}
                    for p in expense.participants
                ],
            }
        )
    return result


def _compute_settlement(trip_id: int, db: Session):
    expense_dicts = _build_expense_dicts(trip_id, db)
    net_balances = settlement.compute_net_balances(expense_dicts)
    transactions = settlement.minimize_transactions(net_balances)

    members = {m.id: m.name for m in db.query(Member).filter(Member.trip_id == trip_id).all()}

    balances = [
        schemas.MemberBalance(
            member_id=member_id,
            member_name=members.get(member_id, "Unknown"),
            net_balance_paise=balance,
        )
        for member_id, balance in net_balances.items()
    ]

    transaction_lines = [
        schemas.SettlementTransaction(
            debtor_id=debtor_id,
            debtor_name=members.get(debtor_id, "Unknown"),
            creditor_id=creditor_id,
            creditor_name=members.get(creditor_id, "Unknown"),
            amount_paise=amount,
        )
        for debtor_id, creditor_id, amount in transactions
    ]

    return balances, transaction_lines


@app.get("/trips/{trip_id}/settlement", response_model=schemas.SettlementOut)
def get_settlement(trip_id: int, db: Session = Depends(get_db)):
    get_trip_or_404(trip_id, db)
    balances, transactions = _compute_settlement(trip_id, db)
    
    # Calculate grand total
    expenses = db.query(Expense).filter(Expense.trip_id == trip_id).all()
    grand_total = sum(e.total_amount_paise for e in expenses)
    
    return schemas.SettlementOut(
        grand_total_paise=grand_total,
        balances=balances,
        transactions=transactions
    )


# ---- Sheet export ----

def _build_trip_sheet(trip_id: int, db: Session) -> schemas.TripSheet:
    trip = get_trip_or_404(trip_id, db)
    members = {m.id: m.name for m in db.query(Member).filter(Member.trip_id == trip_id).all()}
    expenses = db.query(Expense).filter(Expense.trip_id == trip_id).all()

    expense_lines = []
    for expense in expenses:
        participants_data = [
            {"member_id": p.member_id, "share_amount_paise": p.share_amount_paise}
            for p in expense.participants
        ]
        shares = settlement.compute_expense_shares(expense.total_amount_paise, participants_data)

        expense_lines.append(
            schemas.ExpenseSheetLine(
                expense_id=expense.id,
                description=expense.description,
                total_amount_paise=expense.total_amount_paise,
                payers=[
                    schemas.ExpensePayerLine(
                        member_id=p.member_id,
                        member_name=members.get(p.member_id, "Unknown"),
                        amount_paid_paise=p.amount_paid_paise,
                    )
                    for p in expense.payers
                ],
                shares=[
                    schemas.ExpenseShareLine(
                        member_id=member_id,
                        member_name=members.get(member_id, "Unknown"),
                        share_paise=share,
                    )
                    for member_id, share in shares.items()
                ],
            )
        )

    balances, transactions = _compute_settlement(trip_id, db)

    return schemas.TripSheet(
        trip_id=trip.id,
        trip_name=trip.name,
        generated_at=datetime.now(timezone.utc),
        expenses=expense_lines,
        balances=balances,
        transactions=transactions,
    )


@app.get("/trips/{trip_id}/sheet", response_model=schemas.TripSheet)
def get_sheet(trip_id: int, db: Session = Depends(get_db)):
    return _build_trip_sheet(trip_id, db)


def _table_style() -> TableStyle:
    return TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2b2b2b")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#999999")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f2f2f2")]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ])


def _render_sheet_pdf(sheet: schemas.TripSheet) -> BytesIO:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4, 
        title=f"{sheet.trip_name} - Settlement Sheet",
        topMargin=40,
        bottomMargin=40,
        leftMargin=40,
        rightMargin=40
    )
    styles = getSampleStyleSheet()
    story = []

    # Trip name header
    story.append(Paragraph(sheet.trip_name, styles["Title"]))
    generated_ist = sheet.generated_at.astimezone(ZoneInfo("Asia/Kolkata"))
    story.append(
        Paragraph(
            f"Generated: {generated_ist.strftime('%d %b %Y, %I:%M %p IST')}",
            styles["Normal"],
        )
    )
    story.append(Spacer(1, 12))

    # Grand Total Summary Box
    grand_total = sum(e.total_amount_paise for e in sheet.expenses)
    summary_data = [
        ["Trip Total Expenses", f"Rs {grand_total / 100:,.2f}"],
        ["Number of Expenses", str(len(sheet.expenses))],
        ["Number of Members", str(len(set(b.member_id for b in sheet.balances)))],
    ]
    summary_table = Table(summary_data, colWidths=[200, 150], hAlign="LEFT")
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FBF9F4")),
        ("BOX", (0, 0), (-1, -1), 2, colors.HexColor("#E4A93F")),
        ("INNERGRID", (0, 0), (-1, -1), 1, colors.HexColor("#D9D4C7")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (1, 0), (1, 0), 14),
        ("TEXTCOLOR", (1, 0), (1, 0), colors.HexColor("#E4A93F")),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 20))

    # Expenses section
    story.append(Paragraph("Expenses", styles["Heading2"]))
    story.append(Spacer(1, 8))
    
    for line in sheet.expenses:
        story.append(
            Paragraph(
                f"<b>{line.description}</b> - Rs {line.total_amount_paise / 100:.2f}",
                styles["Heading3"],
            )
        )

        payer_rows = [["Paid by", "Amount (Rs)"]]
        for p in line.payers:
            payer_rows.append([p.member_name, f"{p.amount_paid_paise / 100:.2f}"])
        payer_table = Table(payer_rows, colWidths=[180, 100], hAlign="LEFT")
        payer_table.setStyle(_table_style())
        story.append(payer_table)
        story.append(Spacer(1, 6))

        share_rows = [["Participant", "Share (Rs)"]]
        for s in line.shares:
            share_rows.append([s.member_name, f"{s.share_paise / 100:.2f}"])
        share_table = Table(share_rows, colWidths=[180, 100], hAlign="LEFT")
        share_table.setStyle(_table_style())
        story.append(share_table)
        story.append(Spacer(1, 16))

    # Net Balances section
    story.append(Spacer(1, 8))
    story.append(Paragraph("Net Balances", styles["Heading2"]))
    story.append(Spacer(1, 8))
    
    balance_rows = [["Member", "Amount (Rs)", "Status"]]
    for b in sheet.balances:
        amount = b.net_balance_paise / 100
        if amount > 0:
            status = "Gets back"
            row_color = colors.HexColor("#E8F5E9")
        elif amount < 0:
            status = "Owes"
            row_color = colors.HexColor("#FFEBEE")
        else:
            status = "Settled"
            row_color = colors.white
        balance_rows.append([b.member_name, f"{abs(amount):.2f}", status])
    
    balance_table = Table(balance_rows, colWidths=[150, 100, 100], hAlign="LEFT")
    balance_style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F2A3C")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D9D4C7")),
        ("ALIGN", (1, 1), (1, -1), "RIGHT"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ])
    
    # Color rows based on status
    for i, b in enumerate(sheet.balances, start=1):
        amount = b.net_balance_paise / 100
        if amount > 0:
            balance_style.add("BACKGROUND", (0, i), (-1, i), colors.HexColor("#E8F5E9"))
        elif amount < 0:
            balance_style.add("BACKGROUND", (0, i), (-1, i), colors.HexColor("#FFEBEE"))
    
    balance_table.setStyle(balance_style)
    story.append(balance_table)
    story.append(Spacer(1, 20))

    # Settlement Transactions section
    story.append(Paragraph("Settlement Transactions", styles["Heading2"]))
    story.append(Spacer(1, 8))
    
    if sheet.transactions:
        txn_rows = [["From", "To", "Amount (Rs)"]]
        for t in sheet.transactions:
            txn_rows.append([t.debtor_name, t.creditor_name, f"{t.amount_paise / 100:.2f}"])
        txn_table = Table(txn_rows, colWidths=[150, 150, 100], hAlign="LEFT")
        txn_table.setStyle(_table_style())
        story.append(txn_table)
    else:
        story.append(Paragraph("Everyone is already settled.", styles["Normal"]))

    doc.build(story)
    buffer.seek(0)
    return buffer


@app.get("/trips/{trip_id}/sheet/pdf")
def get_sheet_pdf(trip_id: int, db: Session = Depends(get_db)):
    sheet = _build_trip_sheet(trip_id, db)
    pdf_buffer = _render_sheet_pdf(sheet)

    safe_name = sheet.trip_name.replace(" ", "_")
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{safe_name}_settlement.pdf"'},
    )