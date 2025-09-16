import io, pdfplumber
from typing import Dict, Any
from parsers import parse_name, parse_dob, parse_age, parse_report_type, parse_gender
from ocr_utils import render_first_page, deskew_pil
from PIL import ImageOps, ImageFilter
import os, pytesseract
if os.getenv("TESSERACT_CMD"):
    pytesseract.pytesseract.tesseract_cmd = os.getenv("TESSERACT_CMD")
elif os.name == "nt":
    _default = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if os.path.exists(_default):
        pytesseract.pytesseract.tesseract_cmd = _default

def extract_text_fast(pdf_bytes: bytes) -> str:
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        page = pdf.pages[0]
        txt = page.extract_text() or ""
    return txt

def extract_text_ocr(pdf_bytes: bytes) -> str:
    pil = render_first_page(pdf_bytes)
    pil = deskew_pil(pil).convert("L")
    pil = ImageOps.autocontrast(pil)
    pil = pil.filter(ImageFilter.SHARPEN)
    pil = pil.point(lambda x: 0 if x < 180 else 255)
    config = "--oem 3 --psm 4 -l eng"
    return pytesseract.image_to_string(pil, config=config)

def _parse_all(text: str):
    warnings = []
    name = parse_name(text)
    dob  = parse_dob(text)
    age  = parse_age(text)
    gender = parse_gender(text)
    rpt  = parse_report_type(text)

    if not dob and age: warnings.append("DOB missing; inferred from Age")
    if not rpt: warnings.append("Report type not detected")

    found = sum([1 if name else 0, 1 if (dob or age) else 0, 1 if rpt else 0])
    return ({ "patientName": name, "dob": dob, "age": age, "gender": gender, "reportType": rpt }, warnings, found)

def run_pipeline(pdf_bytes: bytes) -> Dict[str, Any]:
    text = extract_text_fast(pdf_bytes)
    used_ocr = False
    if len(text.strip()) < 30:
        used_ocr = True
        text = extract_text_ocr(pdf_bytes)

    fields, warnings, found = _parse_all(text)
    confidence = 0.6 + 0.15*found - (0.1 if used_ocr else 0.0)
    confidence = max(0.0, min(1.0, round(confidence, 2)))

    return {**fields, "confidence": confidence, "warnings": warnings}
