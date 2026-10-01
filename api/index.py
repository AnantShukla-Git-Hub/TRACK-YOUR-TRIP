from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List
from io import BytesIO
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Member(BaseModel):
    id: int
    name: str

class Payer(BaseModel):
    memberId: int
    amount: int

class Expense(BaseModel):
    id: int
    description: str
    amount: int
    payers: List[Payer]
    participants: List[int]

class Balance(BaseModel):
    memberId: int
    amount: int

class Transaction(BaseModel):
    fromId: int
    toId: int
    amount: int

class TripData(BaseModel):
    tripName: str
    members: List[Member]
    expenses: List[Expense]
    balances: List[Balance]
    transactions: List[Transaction]
    totalExpenses: int

def format_rupees(paise):
    return f"Rs {paise / 100:.2f}"

def generate_pdf(data: TripData) -> BytesIO:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    story = []
    
    # Trip header
    story.append(Paragraph(data.tripName, styles["Title"]))
    story.append(Paragraph(
        f"Generated: {datetime.now().strftime('%d %b %Y, %I:%M %p')}",
        styles["Normal"]
    ))
    story.append(Spacer(1, 20))
    
    # Summary box
    summary_data = [
        ["Total Expenses", format_rupees(data.totalExpenses)],
        ["Number of Expenses", str(len(data.expenses))],
        ["Number of Members", str(len(data.members))]
    ]
    summary_table = Table(summary_data, colWidths=[200, 150])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FBF9F4")),
        ("BOX", (0, 0), (-1, -1), 2, colors.HexColor("#E4A93F")),
        ("INNERGRID", (0, 0), (-1, -1), 1, colors.HexColor("#D9D4C7")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (1, 0), (1, 0), 14),
        ("TEXTCOLOR", (1, 0), (1, 0), colors.HexColor("#E4A93F")),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("PADDING", (0, 0), (-1, -1), 8)
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 20))
    
    # Member lookup
    member_map = {m.id: m.name for m in data.members}
    
    # Expenses section
    if data.expenses:
        story.append(Paragraph("Expenses", styles["Heading2"]))
        story.append(Spacer(1, 10))
        
        for exp in data.expenses:
            story.append(Paragraph(
                f"<b>{exp.description}</b> - {format_rupees(exp.amount)}",
                styles["Heading3"]
            ))
            
            payer_rows = [["Paid by", "Amount"]]
            for p in exp.payers:
                payer_rows.append([member_map.get(p.memberId, "Unknown"), format_rupees(p.amount)])
            
            payer_table = Table(payer_rows, colWidths=[180, 100])
            payer_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2b2b2b")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f2f2f2")])
            ]))
            story.append(payer_table)
            story.append(Spacer(1, 15))
    
    # Net balances
    story.append(Paragraph("Net Balances", styles["Heading2"]))
    story.append(Spacer(1, 10))
    
    balance_rows = [["Member", "Amount", "Status"]]
    for b in data.balances:
        amount = b.amount / 100
        if amount > 0:
            status = "Gets back"
        elif amount < 0:
            status = "Owes"
        else:
            status = "Settled"
        balance_rows.append([member_map.get(b.memberId, "Unknown"), f"{abs(amount):.2f}", status])
    
    balance_table = Table(balance_rows, colWidths=[150, 100, 100])
    balance_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F2A3C")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ALIGN", (1, 1), (1, -1), "RIGHT")
    ]))
    story.append(balance_table)
    story.append(Spacer(1, 20))
    
    # Settlement transactions
    story.append(Paragraph("Settlement Transactions", styles["Heading2"]))
    story.append(Spacer(1, 10))
    
    if data.transactions:
        txn_rows = [["From", "To", "Amount"]]
        for t in data.transactions:
            txn_rows.append([
                member_map.get(t.fromId, "Unknown"),
                member_map.get(t.toId, "Unknown"),
                format_rupees(t.amount)
            ])
        
        txn_table = Table(txn_rows, colWidths=[150, 150, 100])
        txn_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2b2b2b")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        story.append(txn_table)
    else:
        story.append(Paragraph("Everyone is settled.", styles["Normal"]))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

@app.post("/api/generate-pdf")
async def generate_trip_pdf(data: TripData):
    try:
        pdf_buffer = generate_pdf(data)
        safe_name = data.tripName.replace(" ", "_")
        
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{safe_name}_settlement.pdf"'}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

handler = app
