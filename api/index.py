# Minimal FastAPI backend for PDF generation only
# This file handles one job: convert trip data to PDF report

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from io import BytesIO
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet

# Create FastAPI app
app = FastAPI()

# Allow all origins for CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all websites to call this API
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

@app.post("/api/generate-pdf")
async def generate_pdf(data: dict):
    """
    Main function that receives trip data and returns PDF file
    Input: JSON with trip name, members, expenses, balances, transactions
    Output: PDF file for download
    """
    try:
        # Create PDF in memory (not saved to disk)
        buffer = BytesIO()
        
        # Set up PDF document with A4 page size
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()  # Get default text styles
        story = []  # List to store all PDF content
        
        # Add trip title
        title = Paragraph(f"<b>{data['tripName']} - Settlement Report</b>", styles['Title'])
        story.append(title)
        
        # Add generation date
        date_text = f"Generated on: {datetime.now().strftime('%d %B %Y at %I:%M %p')}"
        story.append(Paragraph(date_text, styles['Normal']))
        story.append(Paragraph("<br/><br/>", styles['Normal']))  # Add some space
        
        # Create summary table
        total_amount = data.get('totalExpenses', 0)
        num_expenses = len(data.get('expenses', []))
        num_members = len(data.get('members', []))
        
        summary_data = [
            ['Trip Summary', ''],
            ['Total Amount Spent', f'Rs. {total_amount:.2f}'],
            ['Number of Expenses', str(num_expenses)],
            ['Number of Members', str(num_members)]
        ]
        
        summary_table = Table(summary_data)
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),    # Header background
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke), # Header text color
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),             # Left align all text
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), # Bold header
            ('FONTSIZE', (0, 0), (-1, -1), 12),              # Font size
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),          # Header padding
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),  # Data rows background
        ]))
        story.append(summary_table)
        story.append(Paragraph("<br/><br/>", styles['Normal']))
        
        # Add settlement transactions if any exist
        transactions = data.get('transactions', [])
        if transactions:
            story.append(Paragraph("<b>Who Pays Whom:</b>", styles['Heading2']))
            
            # Create member ID to name mapping for easy lookup
            member_names = {m['id']: m['name'] for m in data.get('members', [])}
            
            # Build transactions table
            txn_data = [['From', 'To', 'Amount']]  # Table header
            for txn in transactions:
                from_name = member_names.get(txn['fromId'], 'Unknown')
                to_name = member_names.get(txn['toId'], 'Unknown')
                amount = f"Rs. {txn['amount']:.2f}"
                txn_data.append([from_name, to_name, amount])
            
            txn_table = Table(txn_data)
            txn_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(txn_table)
        else:
            story.append(Paragraph("Everyone is already settled! No payments needed.", styles['Normal']))
        
        # Build the PDF with all content
        doc.build(story)
        buffer.seek(0)  # Reset buffer pointer to beginning
        
        # Create safe filename (remove spaces and special characters)
        safe_filename = data['tripName'].replace(' ', '_').replace('/', '_')
        
        # Return PDF as downloadable file
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={safe_filename}_settlement.pdf"}
        )
        
    except Exception as e:
        # If anything goes wrong, return error message
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

@app.get("/api/health")
def health_check():
    """Simple health check endpoint to test if API is working"""
    return {"status": "API is working!", "timestamp": datetime.now().isoformat()}

# This makes the app work with Vercel serverless functions
handler = app
