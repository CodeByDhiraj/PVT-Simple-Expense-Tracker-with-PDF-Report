import os
from flask import Flask, render_template, request, send_file
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from io import BytesIO

base_dir = os.path.dirname(os.path.abspath(__file__))
# Vercel setup ke liye template folder ka path sahi hona zaroori hai
app = Flask(__name__, template_folder=os.path.join(base_dir, '..', 'templates'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    data = request.json
    user = data.get('name', 'USER')
    items = data.get('items', [])
    month_name = data.get('month', 'OVERALL')
    
    # --- TIER LOGIC (Gamification) ---
    total_spent = sum(float(item['amount']) for item in items)
    
    if total_spent >= 50000:
        tier_name, tier_color = "BLACK INFINITE", "#000000"
    elif total_spent >= 25000:
        tier_name, tier_color = "PLATINUM ELITE", "#334155"
    elif total_spent >= 10000:
        tier_name, tier_color = "GOLD PREFERRED", "#B59410"
    else:
        tier_name, tier_color = "CLASSIC SILVER", "#002366"

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    w, h = A4

    # --- BRANDING HEADER ---
    p.setFillColor(colors.HexColor(tier_color))
    p.rect(0, h-160, w, 160, fill=1, stroke=0)
    
    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 32)
    p.drawString(50, h-60, "ExpensePro")
    
    p.setFont("Helvetica", 10)
    p.drawString(50, h-85, f"STATEMENT | {month_name.upper()} 2026")
    p.drawRightString(w-50, h-60, tier_name)
    
    # Fake Barcode Aesthetic
    p.setFont("Courier", 8)
    p.drawString(50, h-120, "|| |||| ||| ||||| || |||| ||| ||| 4133 31** **** 1012")

    # --- USER & SUMMARY ---
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, h-190, f"ACCOUNT HOLDER: {user.upper()}")
    p.drawRightString(w-50, h-190, f"TOTAL DEBITS: INR {total_spent:,.2f}")

    # --- TABLE HEADER ---
    y = h - 230
    p.setStrokeColor(colors.HexColor(tier_color))
    p.line(40, y, w-40, y)
    p.setFont("Helvetica-Bold", 10)
    p.drawString(55, y-15, "DATE")
    p.drawString(150, y-15, "TRANSACTION DETAILS")
    p.drawRightString(w-55, y-15, "AMOUNT (INR)")
    p.line(40, y-20, w-40, y-20)

    # --- TRANSACTIONS ---
    y -= 40
    p.setFont("Helvetica", 10)
    for i, item in enumerate(items):
        if y < 80:
            p.showPage()
            y = h - 50
        
        if i % 2 == 0:
            p.setFillColor(colors.HexColor("#f8fafc"))
            p.rect(40, y-5, w-80, 18, fill=1, stroke=0)
        
        p.setFillColor(colors.black)
        p.drawString(55, y, str(item['date']))
        p.drawString(150, y, str(item['category']))
        p.drawRightString(w-55, y, f"{float(item['amount']):,.2f}")
        y -= 22

    # --- FOOTER ---
    p.line(350, y, w-40, y)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(350, y-25, "NET SPEND:")
    p.drawRightString(w-55, y-25, f"INR {total_spent:,.2f}")

    p.showPage()
    p.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"Statement_{month_name}.pdf")

if __name__ == "__main__":
    app.run(debug=True)