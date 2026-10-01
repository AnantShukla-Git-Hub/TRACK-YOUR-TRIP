# Vercel serverless function: detailed trip settlement PDF (ReportLab).
# Same request/response contract as before: POST JSON -> PDF bytes.

from http.server import BaseHTTPRequestHandler
import json
import re
from io import BytesIO
from datetime import datetime
from xml.sax.saxutils import escape
from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Table, TableStyle,
                                Spacer, CondPageBreak)
from reportlab.graphics.shapes import Drawing, Rect

# ---------- palette ----------
INK, GREEN, YELLOW = HexColor('#1F2A24'), HexColor('#1E5B45'), HexColor('#E8B931')
MUTED, RULE, TINT = HexColor('#5C6A62'), HexColor('#CBD0C8'), HexColor('#E4EFE9')
SAND, BRICK, ORANGE = HexColor('#FBF1CF'), HexColor('#B8503A'), HexColor('#E07A2F')
MCOL = [HexColor(c) for c in ('#1E5B45', '#E07A2F', '#B5446E', '#6D4C7D',
                              '#C9A227', '#7A8B2E', '#B8503A', '#5E9E7E')]
CATS = {'Stay': '#6D4C7D', 'Food': '#E07A2F', 'Travel': '#1E5B45', 'Fuel': '#B8503A',
        'Entry tickets': '#B5446E', 'Shopping': '#7A8B2E', 'Other': '#8A948D'}
W = 170 * mm


# ---------- small helpers ----------
def clean(s):
    # Built-in PDF fonts are Latin-1 only; avoid garbage glyphs for other scripts
    return str(s).encode('latin-1', 'replace').decode('latin-1')


def esc(s):
    return escape(clean(s))


def inr(x):
    """Rs. 1,23,456.50 (Indian digit grouping)."""
    cents = int(round(abs(float(x)) * 100))
    whole, frac = divmod(cents, 100)
    s = str(whole)
    if len(s) > 3:
        head, tail, parts = s[:-3], s[-3:], []
        while len(head) > 2:
            parts.insert(0, head[-2:])
            head = head[:-2]
        if head:
            parts.insert(0, head)
        s = ','.join(parts + [tail])
    return ('- ' if x < 0 and cents else '') + f'Rs. {s}.{frac:02d}'


def fdate(d):
    try:
        return datetime.strptime(str(d)[:10], '%Y-%m-%d').strftime('%d %b %Y')
    except Exception:
        return '-'


def S(name, size=8.5, bold=False, color=INK, align=0, lead=None):
    return ParagraphStyle(name, fontName='Helvetica-Bold' if bold else 'Helvetica',
                          fontSize=size, leading=lead or size * 1.35,
                          textColor=color, alignment=align)


def P(text, size=8.5, bold=False, color=INK, align=0, lead=None):
    return Paragraph(text, S('x', size, bold, color, align, lead))


def heading(text, color=GREEN):
    t = Table([['', P(esc(text), 13, True, INK)]], colWidths=[3 * mm, W - 3 * mm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), color), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (1, 0), (1, 0), 8), ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4)]))
    return [Spacer(1, 7 * mm), t, Spacer(1, 3 * mm)]


def base_style(n_rows, extra=()):
    st = [('BACKGROUND', (0, 0), (-1, 0), GREEN), ('BOX', (0, 0), (-1, -1), 1, GREEN),
          ('LINEBELOW', (0, 1), (-1, -1), 0.4, RULE), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
          ('TOPPADDING', (0, 0), (-1, -1), 5), ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
          ('LEFTPADDING', (0, 0), (-1, -1), 6), ('RIGHTPADDING', (0, 0), (-1, -1), 6),
          ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor('#F4F7F3')])]
    return TableStyle(st + list(extra))


# ---------- page decoration: double border, corner marks, colour stripe, footer ----------
def decorate(c, doc, name):
    w, h = A4
    m = 8 * mm
    c.saveState()
    c.setStrokeColor(GREEN)
    c.setLineWidth(2.2)
    c.rect(m, m, w - 2 * m, h - 2 * m)
    c.setStrokeColor(YELLOW)
    c.setLineWidth(0.7)
    c.rect(m + 2.4 * mm, m + 2.4 * mm, w - 2 * m - 4.8 * mm, h - 2 * m - 4.8 * mm)
    c.setFillColor(YELLOW)
    c.setStrokeColor(GREEN)
    c.setLineWidth(1)
    for x in (m, w - m):
        for y in (m, h - m):
            c.rect(x - 2 * mm, y - 2 * mm, 4 * mm, 4 * mm, fill=1, stroke=1)
    seg = (w - 2 * m - 24 * mm) / len(MCOL)
    for i, col in enumerate(MCOL):
        c.setFillColor(col)
        c.rect(m + 12 * mm + i * seg, h - m - 7.5 * mm, seg, 1.6 * mm, stroke=0, fill=1)
    c.setFillColor(MUTED)
    c.setFont('Helvetica', 7.5)
    c.drawString(m + 12 * mm, m + 6 * mm, f'{clean(name)}  |  Settlement report')
    c.drawRightString(w - m - 12 * mm, m + 6 * mm, f'Page {doc.page}')
    c.restoreState()


# ---------- report ----------
def build_pdf(data):
    members = data.get('members', [])
    expenses = data.get('expenses', [])
    txns = data.get('transactions', [])
    name = str(data.get('tripName') or 'Trip')
    idx = {m['id']: i for i, m in enumerate(members)}
    mn = {m['id']: m['name'] for m in members}
    col = lambda mid: MCOL[idx.get(mid, 0) % len(MCOL)]

    # paid / share per member (equal split among participants, same as the app)
    tot = {m['id']: {'paid': 0.0, 'share': 0.0} for m in members}
    for e in expenses:
        parts = e.get('participants') or []
        share = e['amount'] / len(parts) if parts else 0
        for p in e.get('payers', []):
            if p['memberId'] in tot:
                tot[p['memberId']]['paid'] += p['amount']
        for pid in parts:
            if pid in tot:
                tot[pid]['share'] += share
    total = sum(e['amount'] for e in expenses)
    now = datetime.now().strftime('%d %B %Y, %I:%M %p')

    story = [Paragraph(esc(name), S('t', 30, True, GREEN, lead=34)),
             P('Trip settlement report', 12, False, MUTED), P(f'Generated {now}', 7.5, False, MUTED),
             Spacer(1, 6 * mm)]

    # summary cards
    cards = [('Total trip cost', inr(total), GREEN),
             ('Average per person', inr(total / max(1, len(members))), ORANGE),
             ('Expenses logged', str(len(expenses)), MCOL[2]),
             ('Members', str(len(members)), MCOL[3])]
    t = Table([[[P(a, 7.5, False, MUTED), P(b, 14, True, c, lead=18)] for a, b, c in cards]],
              colWidths=[W / 4] * 4)
    st = [('BOX', (0, 0), (-1, -1), 0.8, RULE), ('INNERGRID', (0, 0), (-1, -1), 0.5, RULE),
          ('TOPPADDING', (0, 0), (-1, -1), 8), ('BOTTOMPADDING', (0, 0), (-1, -1), 9),
          ('LEFTPADDING', (0, 0), (-1, -1), 9), ('VALIGN', (0, 0), (-1, -1), 'TOP')]
    st += [('LINEABOVE', (i, 0), (i, 0), 3.5, c[2]) for i, c in enumerate(cards)]
    t.setStyle(TableStyle(st))
    story.append(t)

    # who paid / owes what
    story += heading('Who paid and who owes')
    rows = [['', P('Member', 8.5, True, white), P('Total paid', 8.5, True, white, 2),
             P('Fair share', 8.5, True, white, 2), P('Balance', 8.5, True, white, 2)]]
    extra = []
    for i, m in enumerate(members, 1):
        a = tot[m['id']]
        net = a['paid'] - a['share']
        txt, c = (('Settled', MUTED) if abs(net) <= 1 else
                  (('Gets back ' + inr(net), GREEN) if net > 0 else ('Owes ' + inr(-net), BRICK)))
        rows.append(['', P(esc(m['name']), 9, True), P(inr(a['paid']), 8.5, False, INK, 2),
                     P(inr(a['share']), 8.5, False, INK, 2), P(txt, 8.5, True, c, 2)])
        extra.append(('BACKGROUND', (0, i), (0, i), col(m['id'])))
    rows.append(['', P('Trip total', 9, True), P(inr(sum(a['paid'] for a in tot.values())), 8.5, True, INK, 2),
                 P(inr(sum(a['share'] for a in tot.values())), 8.5, True, INK, 2), ''])
    n = len(rows) - 1
    extra += [('BACKGROUND', (0, n), (-1, n), SAND), ('LINEABOVE', (0, n), (-1, n), 1, GREEN)]
    t = Table(rows, colWidths=[4 * mm, 52 * mm, 36 * mm, 36 * mm, 42 * mm], repeatRows=1)
    t.setStyle(base_style(len(rows), extra))
    story.append(t)

    # final settlement as ticket stubs
    story += heading('Final settlement', YELLOW)
    if txns:
        for x in txns:
            f, to = mn.get(x['fromId'], 'Unknown'), mn.get(x['toId'], 'Unknown')
            tb = Table([[[P('From', 7.5, False, MUTED), P(esc(f), 13, True, lead=16)],
                         P('pays', 9, False, MUTED, 1),
                         [P('To', 7.5, False, MUTED), P(esc(to), 13, True, lead=16)],
                         [P('Amount', 7.5, False, MUTED), P(inr(x['amount']), 14, True, GREEN, lead=18)]]],
                       colWidths=[52 * mm, 24 * mm, 52 * mm, 42 * mm])
            tb.setStyle(TableStyle([
                ('BOX', (0, 0), (-1, -1), 1.2, GREEN), ('BACKGROUND', (3, 0), (3, 0), SAND),
                ('LINEBEFORE', (3, 0), (3, 0), 1, GREEN, 1, (3, 3)), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 8), ('BOTTOMPADDING', (0, 0), (-1, -1), 9),
                ('LEFTPADDING', (0, 0), (-1, -1), 12)]))
            story += [CondPageBreak(30 * mm), tb, Spacer(1, 3 * mm)]
        story.append(P(f'{len(txns)} payment{"s" if len(txns) != 1 else ""} settle every balance in this trip.',
                       8, False, MUTED))
    else:
        story.append(P('Everyone is already settled. No payments needed.', 9.5, True, GREEN))

    # category breakdown with bars
    cats = {}
    for e in expenses:
        k = e.get('category') or 'Other'
        c = cats.setdefault(k, [0, 0.0])
        c[0] += 1
        c[1] += e['amount']
    if cats:
        story += heading('Spending by category', ORANGE)
        rows = [['', P('Category', 8.5, True, white), P('Entries', 8.5, True, white, 2),
                 P('Amount', 8.5, True, white, 2), P('Share', 8.5, True, white, 2), '']]
        extra = []
        for i, (k, (cnt, amt)) in enumerate(sorted(cats.items(), key=lambda kv: -kv[1][1]), 1):
            pct = amt / total if total else 0
            cc = HexColor(CATS.get(k, '#8A948D'))
            d = Drawing(54 * mm, 4 * mm)
            d.add(Rect(0, 0, 54 * mm, 4 * mm, fillColor=HexColor('#ECEFEA'), strokeColor=None))
            d.add(Rect(0, 0, 54 * mm * pct, 4 * mm, fillColor=cc, strokeColor=None))
            rows.append(['', P(esc(k), 9, True), P(str(cnt), 8.5, False, INK, 2), P(inr(amt), 8.5, False, INK, 2),
                         P(f'{pct * 100:.0f}%', 8.5, False, INK, 2), d])
            extra.append(('BACKGROUND', (0, i), (0, i), cc))
        t = Table(rows, colWidths=[4 * mm, 36 * mm, 20 * mm, 34 * mm, 16 * mm, 60 * mm], repeatRows=1)
        t.setStyle(base_style(len(rows), extra))
        story.append(t)

    # full expense ledger
    story += heading('Expense ledger', MCOL[2])
    rows = [['', P('Date', 8, True, white), P('Expense', 8, True, white), P('Paid by', 8, True, white),
             P('Split among', 8, True, white), P('Per head', 8, True, white, 2), P('Amount', 8, True, white, 2)]]
    extra = []
    for i, e in enumerate(expenses, 1):
        parts = e.get('participants') or []
        k = e.get('category') or 'Other'
        cc = CATS.get(k, '#8A948D')
        paid = '<br/>'.join(f'{esc(mn.get(p["memberId"], "?"))}: {inr(p["amount"])}' for p in e.get('payers', []))
        split = 'Everyone' if len(parts) == len(members) else ', '.join(esc(mn.get(p, '?')) for p in parts)
        rows.append(['', P(fdate(e.get('date')), 7.5),
                     [P(f'{i}. {esc(e["description"])}', 8.5, True),
                      P(f'<font color="{cc}">{esc(k)}</font>', 7.5)],
                     P(paid, 7.5), P(f'{split} ({len(parts)})', 7.5),
                     P(inr(e['amount'] / len(parts)) if parts else '-', 7.5, False, INK, 2),
                     P(inr(e['amount']), 8.5, True, INK, 2)])
        extra.append(('BACKGROUND', (0, i), (0, i), HexColor(cc)))
    rows.append(['', '', P('Trip total', 8.5, True), '', '', '', P(inr(total), 9, True, GREEN, 2)])
    n = len(rows) - 1
    extra += [('BACKGROUND', (0, n), (-1, n), SAND), ('LINEABOVE', (0, n), (-1, n), 1, GREEN)]
    t = Table(rows, colWidths=[3 * mm, 19 * mm, 42 * mm, 40 * mm, 29 * mm, 17 * mm, 20 * mm], repeatRows=1)
    t.setStyle(base_style(len(rows), extra))
    story.append(t)

    # personal statements
    for m in members:
        mid = m['id']
        a = tot[mid]
        story += [CondPageBreak(70 * mm)] + heading(f'Statement: {m["name"]}', col(mid))
        rows = [[P('Expense', 8, True, white), P('Date', 8, True, white), P('Paid', 8, True, white, 2),
                 P('Share', 8, True, white, 2), P('Running balance', 8, True, white, 2)]]
        run = 0.0
        for e in expenses:
            parts = e.get('participants') or []
            paid = sum(p['amount'] for p in e.get('payers', []) if p['memberId'] == mid)
            sh = e['amount'] / len(parts) if mid in parts else 0
            if not paid and mid not in parts:
                continue
            run += paid - sh
            rows.append([[P(esc(e['description']), 8.5, True), P(esc(e.get('category') or 'Other'), 7.5, False, MUTED)],
                         P(fdate(e.get('date')), 7.5), P(inr(paid) if paid else '-', 8, False, INK, 2),
                         P(inr(sh) if sh else '-', 8, False, INK, 2),
                         P(inr(run), 8, True, GREEN if run >= 0 else BRICK, 2)])
        net = a['paid'] - a['share']
        rows.append([P('Totals', 8.5, True), '', P(inr(a['paid']), 8.5, True, INK, 2),
                     P(inr(a['share']), 8.5, True, INK, 2),
                     P(('Gets back ' if net > 0 else 'Owes ') + inr(abs(net)) if abs(net) > 1 else 'Settled',
                       8.5, True, GREEN if net >= 0 else BRICK, 2)])
        n = len(rows) - 1
        t = Table(rows, colWidths=[62 * mm, 22 * mm, 28 * mm, 28 * mm, 30 * mm], repeatRows=1)
        t.setStyle(base_style(len(rows), [('BACKGROUND', (0, 0), (-1, 0), col(mid)),
                                          ('BOX', (0, 0), (-1, -1), 1, col(mid)),
                                          ('BACKGROUND', (0, n), (-1, n), SAND),
                                          ('LINEABOVE', (0, n), (-1, n), 1, col(mid))]))
        story.append(t)

    story += [Spacer(1, 8 * mm),
              P('Costs are split equally among the selected participants. Amounts are rounded to two '
                'decimals and balances under Rs. 1 are treated as settled.', 7.5, False, MUTED)]

    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=20 * mm, rightMargin=20 * mm,
                            topMargin=24 * mm, bottomMargin=20 * mm, title=f'{clean(name)} - Settlement report')
    deco = lambda c, d: decorate(c, d, name)
    doc.build(story, onFirstPage=deco, onLaterPages=deco)
    buf.seek(0)
    return buf


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle POST request to generate PDF"""
        try:
            content_length = int(self.headers['Content-Length'])
            data = json.loads(self.rfile.read(content_length).decode('utf-8'))
            pdf_buffer = self.generate_pdf(data)

            self.send_response(200)
            self.send_header('Content-Type', 'application/pdf')
            # Safe ASCII filename (special chars / Hindi in trip name would crash headers)
            safe_name = re.sub(r'[^A-Za-z0-9_-]+', '_', str(data.get('tripName', 'trip'))).strip('_') or 'trip'
            self.send_header('Content-Disposition', f'attachment; filename="{safe_name}_settlement.pdf"')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(pdf_buffer.getvalue())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))

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
            self.wfile.write(json.dumps({"status": "API is working!",
                                         "timestamp": datetime.now().isoformat()}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def generate_pdf(self, data):
        """Generate PDF from trip data"""
        return build_pdf(data)
