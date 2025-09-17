### LabRead Lite — Lab Report Header Extract (PoC)

A small proof‑of‑concept built to demonstrate systems thinking and coding skills in a constrained timeframe. The service extracts key header fields from the first page of a lab report PDF and returns structured JSON.

- Extracted fields: Patient Name, DOB (or Age), Gender, Report Type
- Output includes: confidence score and warnings
- API: FastAPI with an interactive UI at `/docs`

---

## Problem Statement

Given a limited time window, build a simple service that:
- Accepts a lab report PDF upload
- Extracts header fields (Name, DOB/Age, Gender, Report Type) from the first page
- Returns structured JSON with a coarse confidence estimate and any warnings
- Exposes a minimal, self‑documenting API

This is intentionally a PoC: correctness, coverage, and polish are secondary to demonstrating approach and structure.

---

## Approach

- Dual text extraction:
  - Try fast, text‑based extraction via `pdfplumber`
  - If text is sparse, fall back to OCR:
    - Render first page with `pymupdf` at high DPI
    - Light preprocessing (deskew, grayscale, thresholding, sharpen)
    - Run `pytesseract` (Tesseract OCR) with `--psm 4`
- Heuristic parsing:
  - Regex‑based detection for Name, DOB, Age, Gender
  - Keyword/alias matching for common report types (e.g., CBC, CMP, HbA1c)
  - Date normalization to `YYYY-MM-DD`
- Confidence heuristic:
  - Base confidence adjusted by number of fields found and whether OCR fallback was needed
- API:
  - `POST /extract` with multipart PDF upload
  - `GET /` service info
  - `GET /health` liveness
  - Interactive docs at `/docs`

Directory highlights:
- `app.py` — FastAPI app and endpoints
- `extractor.py` — pipeline orchestration (text extraction, OCR fallback, confidence, warnings)
- `parsers.py` — field parsers and normalization
- `ocr_utils.py` — rendering and image preprocessing
- `models.py` — response schema
- `sample_pdfs/` — example inputs
- `tests/` — quick script to exercise the flow

---

## Tools & Technologies

- FastAPI, Uvicorn
- PDF text: `pdfplumber`
- PDF rendering: `pymupdf` (fitz)
- OCR: `pytesseract` + Tesseract OCR
- Image preprocessing: OpenCV (headless), Pillow
- Data modeling: Pydantic

See `requirements.txt` for exact dependencies.

---

## Assumptions

- Only the first page header contains the required fields.
- PDFs are either digital-text or reasonably OCR‑able scans.
- Date formats are limited to common US/international styles and normalized to `YYYY-MM-DD`.
- No persistence or authentication required for the PoC.
- Performance constraints are modest (single‑process local run is sufficient).

---

## Trade‑offs

- Regex/keyword heuristics instead of ML or layout‑aware parsing.
- OCR quality is dependent on scan quality; minimal image preprocessing is applied.
- Confidence is a coarse heuristic, not a model‑based probability.
- No UI beyond FastAPI’s auto‑generated `/docs`.
- No concurrency tuning, metrics, or tracing in this PoC.

---

## Prerequisites

- Python 3.10+ recommended
- Tesseract OCR installed and available on PATH (or configure `TESSERACT_CMD`)
- OS packages:
  - Windows/macOS/Linux supported; OpenCV is installed via wheels (`opencv-python-headless`)

### Install Tesseract OCR

- Windows (recommended installer):
  - Download from `https://github.com/UB-Mannheim/tesseract/wiki`
  - Default path: `C:\Program Files\Tesseract-OCR\tesseract.exe`
- macOS (Homebrew):
  - `brew install tesseract`
- Ubuntu/Debian:
  - `sudo apt-get update && sudo apt-get install -y tesseract-ocr`

If Tesseract is not on PATH, set the environment variable `TESSERACT_CMD`:

- Windows PowerShell:
  - `$env:TESSERACT_CMD="C:\Program Files\Tesseract-OCR\tesseract.exe"`
- macOS/Linux (bash/zsh):
  - `export TESSERACT_CMD=/usr/local/bin/tesseract`  (adjust path as needed)

The code auto-detects the default Windows path if present.

---

## Setup & Run

1) Clone and enter the project:

2) Create and activate a virtual environment:

- Windows PowerShell:
```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
```

- macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

3) Install dependencies:
```bash
pip install -r requirements.txt
```

4) Ensure Tesseract is installed and accessible (see Prerequisites). Optionally set `TESSERACT_CMD` (if not on PATH):
```powershell
# Windows example
$env:TESSERACT_CMD="C:\Program Files\Tesseract-OCR\tesseract.exe"
```
```bash
# macOS/Linux example
export TESSERACT_CMD=/usr/local/bin/tesseract
