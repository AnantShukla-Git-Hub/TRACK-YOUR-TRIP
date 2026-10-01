# Simple Vercel serverless function for PDF generation
# This file works directly with Vercel's Python runtime

from http.server import BaseHTTPRequestHandler
import json
from io import BytesIO
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle POST request to generate PDF"""
        try:
            # Read the request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Generate PDF
            pdf_buffer = self.generate_pdf(data)
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/pdf')
            self.send_header('Content-Disposition', f'attachment; filename="{data["tripName"]}_settlement.pdf"')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # Send PDF content
            self.wfile.write(pdf_buffer.getvalue())
            
        except Exception as e:
            # Send error response
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            error_response = json.dumps({"error": str(e)})
            self.wfile.write(error_response.encode('utf-8'))
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET request for health check"""
        if self.path == '/api/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = json.dumps({
                "status": "API is working!", 
                "timestamp": datetime.now().isoformat()
            })
            self.wfile.write(response.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def generate_pdf(self, data):
        """Generate PDF from trip data"""
        buffer = BytesIO()
        
        # Set up PDF document
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Add title
        title = Paragraph(f"<b>{data['tripName']} - Settlement Report</b>", styles['Title'])
        story.append(title)
        
        # Add date
        date_text = f"Generated on: {datetime.now().strftime('%d %B %Y at %I:%M %p')}"
        story.append(Paragraph(date_text, styles['Normal']))
        story.append(Paragraph("<br/><br/>", styles['Normal']))
        
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
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ]))
        story.append(summary_table)
        story.append(Paragraph("<br/><br/>", styles['Normal']))
        
        # Add transactions
        transactions = data.get('transactions', [])
        if transactions:
            story.append(Paragraph("<b>Who Pays Whom:</b>", styles['Heading2']))
            
            member_names = {m['id']: m['name'] for m in data.get('members', [])}
            
            txn_data = [['From', 'To', 'Amount']]
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
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        return buffer
