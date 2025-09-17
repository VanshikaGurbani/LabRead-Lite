### LabRead Lite — Lab Report Header Extract (PoC)

A small proof‑of‑concept built to demonstrate systems thinking and coding skills in a constrained timeframe. The service extracts key header fields from the first page of a lab report PDF and returns structured JSON.

- Extracted fields: Patient Name, DOB (or Age), Gender, Report Type
- Output includes: confidence score and warnings
- API: FastAPI with an interactive UI at `/docs`

---

## Problem Statement

Build a lightweight service that:
- Accepts a lab report PDF upload
- Extracts header fields: **Patient Name, DOB (or Age), Gender, Report Type**
- Returns structured JSON with a confidence score and warnings
- Exposes a minimal API for quick evaluation

This is intentionally a PoC: correctness, coverage, and polish are secondary to demonstrating approach and structure.

---

## Approach

- Dual text extraction:
  - First attempt: Fast text-based extraction via `pdfplumber`
  - Fallback: OCR processing when text extraction yields insufficient results:
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

## Project Structure

```text
labread-lite/
├─ sample_pdfs/        # Official 5 test PDFs for evaluation
├─ tests/              # Test scripts
│  ├─ test_runner.py   # Runs extraction on all sample PDFs
│  └─ make_samples.py  # Generates synthetic sample PDFs (via reportlab)
├─ .gitignore          # Ignore rules (venv, cache, outputs)
├─ README.md           # Project documentation
├─ app.py              # FastAPI app and endpoints
├─ extractor.py        # Pipeline: text extraction + OCR fallback + parsing
├─ models.py           # Response schema
├─ ocr_utils.py        # Image rendering and preprocessing
├─ out.txt             # Example output log (optional)
├─ parsers.py          # Regex parsers for fields
└─ requirements.txt    # Python dependencies
```
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

1) Clone and enter the project

2) Create and activate a virtual environment:

- Windows PowerShell:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
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
```

5) Run the API:
```bash
uvicorn app:app --reload
```

6) Open the interactive API docs:
- Browser: `http://127.0.0.1:8000/`
- **Important**: Add `/docs` to the URL to access Swagger UI: `http://127.0.0.1:8000/docs`

7) Test the API using Swagger UI:
- In the Swagger UI, expand the `POST /extract` endpoint
- Click "Try it out"
- Click "Choose File" and select a PDF from `sample_pdfs/` folder
- Click "Execute" to test the extraction

8) Alternative: Test via terminal:
```bash
python tests/test_runner.py
```

9) Alternative: Test via curl:
```bash
curl -X POST "http://127.0.0.1:8000/extract" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample_pdfs/1_clean.pdf"
```

Expected JSON (example):
```json
{
  "patientName": "Jane A. Doe",
  "dob": "1982-07-03",
  "age": 42,
  "gender": null,
  "reportType": "Comprehensive Metabolic Panel",
  "confidence": 0.82,
  "warnings": ["DOB missing; inferred from Age"]
}
```

---

## What I'd Improve with More Time

- More robust parsing using layout cues (coordinates, fonts) and named‑entity recognition.
- Better confidence calibration with per‑field quality signals and training data.
- Support multi‑page heuristics and cross‑checks (e.g., header + footer consistency).
- Expand report type ontology and fuzzy matching.
- Batch and async processing, plus basic observability (metrics, logs, tracing).
- Containerization (Dockerfile) and CI to run tests and linting.
- Security hardening (file size/type limits, rate limiting).

---

## Notes for the Reviewer

- This is an intentionally lean PoC focused on approach and structure over polish.
- The code prefers clarity and explicit steps for easy review and iteration.
- Sample PDFs are provided in `sample_pdfs/` for quick evaluation.
