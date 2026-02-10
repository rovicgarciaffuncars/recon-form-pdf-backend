from flask import Flask, request, send_file
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader, PdfWriter
import io
import datetime

app = Flask(__name__)

TEMPLATE_PATH = "template.pdf"

# --- FIELD COORDINATES (PAGE 1) ---
FIELD_MAP = {
    "vin": (60, 735),
    "odometer": (250, 735),
    "stock_number": (430, 735),
    "tech_name": (60, 710),
}

# Example Pass | Note | Fail positions
PNF_MAP = {
    "dc_wipers": {"pass": (400, 650), "note": (450, 650), "fail": (500, 650)},
    "dc_defrosters": {"pass": (400, 630), "note": (450, 630), "fail": (500, 630)},
    "dc_glass": {"pass": (400, 610), "note": (450, 610), "fail": (500, 610)},
    "dc_horn": {"pass": (400, 590), "note": (450, 590), "fail": (500, 590)},
}

@app.route("/generate-pdf", methods=["POST"])
def generate_pdf():
    data = request.json

    # --- Create overlay PDF ---
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)

    # HEADER TEXT
    for field, coords in FIELD_MAP.items():
        value = data.get(field)
        if value:
            can.drawString(coords[0], coords[1], str(value))

    # PASS / NOTE / FAIL CHECKMARKS
    for field, options in PNF_MAP.items():
        status = data.get(field)
        if status in options:
            x, y = options[status]
            can.drawString(x, y, "✔")

    can.save()
    packet.seek(0)

    # --- Merge overlay with template ---
    overlay = PdfReader(packet)
    template = PdfReader(TEMPLATE_PATH)

    writer = PdfWriter()
    page = template.pages[0]
    page.merge_page(overlay.pages[0])
    writer.add_page(page)

    # --- Output final PDF ---
    output = io.BytesIO()
    writer.write(output)
    output.seek(0)

    # --- Dynamic filename ---
    today = datetime.date.today().isoformat()
    filename = f"FFUN_Recon_{data.get('vin','UNKNOWN')}_{data.get('tech_name','TECH')}_{today}.pdf"

    return send_file(
        output,
        as_attachment=True,
        download_name=filename,
        mimetype="application/pdf"
    )

@app.route("/")
def health():
    return {"status": "ok"}
