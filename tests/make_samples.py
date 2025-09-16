# Generates 5 PHI-safe sample PDFs into sample_pdfs/

import os, io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from PIL import Image, ImageDraw, ImageFont

OUT_DIR = "sample_pdfs"
os.makedirs(OUT_DIR, exist_ok=True)

def make_text_pdf(path, lines, rotate_deg=0):
    c = canvas.Canvas(path, pagesize=LETTER)
    w, h = LETTER
    if rotate_deg:
        c.translate(w/2, h/2); c.rotate(rotate_deg); c.translate(-w/2, -h/2)
    y = h - 1*inch
    for line in lines:
        c.drawString(1*inch, y, line); y -= 14
    c.showPage(); c.save()

def make_scanned_pdf(path, lines, rotate_deg=9):
    # Build an image with text, rotate (to mimic a scanned/skewed page), then embed into a PDF
    W, H = 2550, 3300  # ~8.5x11in @300dpi
    img = Image.new("L", (W, H), 255)
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 40)
    except:
        font = ImageFont.load_default()
    y = 300
    for line in lines:
        draw.text((200, y), line, fill=0, font=font); y += 60
    img = img.rotate(rotate_deg, expand=True, fillcolor=255).convert("RGB")

    buf = io.BytesIO(); img.save(buf, format="PNG"); buf.seek(0)
    c = canvas.Canvas(path, pagesize=LETTER)
    w, h = LETTER
    reader = ImageReader(buf); iw, ih = img.size
    scale = (w-2*inch)/iw; new_w, new_h = iw*scale, ih*scale
    x, y = (w-new_w)/2, (h-new_h)/2
    c.drawImage(reader, x, y, width=new_w, height=new_h)
    c.showPage(); c.save()

# 1) Clean header — all fields present
make_text_pdf(os.path.join(OUT_DIR, "1_clean.pdf"), [
  "Patient Name: Jane A. Doe",
  "DOB: 1982-07-03",
  "Report Type: Comprehensive Metabolic Panel"
])

# 2) DoB label variant + acronym panel
make_text_pdf(os.path.join(OUT_DIR, "2_DoB_variant.pdf"), [
  "Patient: John Q. Public",
  "DoB - 07/03/1982",
  "Panel: CMP"
])

# 3) Age only (no DOB) + Lipid Panel
make_text_pdf(os.path.join(OUT_DIR, "3_age_only.pdf"), [
  "Patient Name: Alex Roe",
  "Age: 42 years",
  "Test: Lipid Panel"
])

# 4) Scanned/skewed (forces OCR later)
make_scanned_pdf(os.path.join(OUT_DIR, "4_scanned_skewed.pdf"), [
  "Patient Name: Mira L. Tan",
  "DOB: 1990-11-12",
  "Profile: HbA1c"
], rotate_deg=9)

# 5) Missing report type (should return warning)
make_text_pdf(os.path.join(OUT_DIR, "5_missing_report.pdf"), [
  "Patient Name: Sam Kim",
  "DOB: 01-12-1989"
])

print("Created PDFs in sample_pdfs/:")
for f in sorted(os.listdir(OUT_DIR)):
    if f.lower().endswith(".pdf"):
        print(" -", f)
print("Done.")