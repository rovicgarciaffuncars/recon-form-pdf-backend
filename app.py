from flask import Flask, request, send_file
from pdfrw import PdfReader, PdfWriter, PdfDict
import tempfile
import os

app = Flask(__name__)

TEMPLATE_PATH = "template.pdf"

@app.route("/generate-pdf", methods=["POST"])
def generate_pdf():
    data = request.json

    template = PdfReader(TEMPLATE_PATH)
    for page in template.pages:
        if page.Annots:
            for annot in page.Annots:
                if annot.T:
                    key = annot.T[1:-1]
                    if key in data:
                        annot.V = PdfDict(V=str(data[key]))
                        annot.AP = None

    output = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    PdfWriter().write(output.name, template)

    return send_file(
        output.name,
        as_attachment=True,
        download_name="FFUN_Recon_Completed.pdf"
    )

@app.route("/")
def health():
    return {"status": "ok"}
