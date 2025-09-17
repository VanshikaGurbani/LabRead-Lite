# LabRead Lite — Lab Report Header Extract (PoC)

This is a **Proof of Concept (PoC)** project that extracts patient header fields from lab report PDFs into structured JSON.  
It demonstrates the feasibility of parsing **basic metadata** from both **digital PDFs** and **scanned PDFs** using a minimal, testable pipeline.

---

## 🎯 Goal & Scope
- **Goal**: Extract `Patient Name`, `DOB (or Age)`, and `Report Type` from the **first page** of lab reports.  
- **Output**: JSON with confidence score and warnings.  
- **Scope**:  
  - Works on **first page only**.  
  - Handles **synthetic PDFs** provided in `sample_pdfs/`.  
  - Optional OCR (via Tesseract) for scanned/skewed reports.  
  - Graceful handling of missing fields (via warnings).

---

## 🏗️ Approach
1. **PDF to Text**  
   - Try `pdfplumber` for direct text extraction.  
   - If text is too sparse, fallback to OCR (PyMuPDF render + deskew + Tesseract).  

2. **Parsing**  
   - Regex rules for patient name, DOB, age, and report type.  
   - Normalizes DOB (`YYYY-MM-DD`) and resolves acronyms (e.g., `CBC → Complete Blood Count`).  

3. **Output**  
   - JSON object with fields, confidence score, and warnings.  
   - Example:  
     ```json
     {
       "patientName": "Jane A. Doe",
       "dob": "1982-07-03",
       "age": null,
       "reportType": "Comprehensive Metabolic Panel",
       "confidence": 1.0,
       "warnings": []
     }
     ```

---

## 📂 Project Structure
```text
labread-lite/
├─ app.py               # FastAPI app (POST /extract)
├─ extractor.py         # Pipeline: PDF → text/OCR → parse → JSON
├─ parsers.py           # Regex-based field extraction
├─ ocr_utils.py         # OCR preprocessing helpers
├─ models.py            # Pydantic response schema
├─ tests/
│  └─ test_runner.py    # Runs extraction on sample PDFs
├─ sample_pdfs/         # Synthetic test PDFs
│  ├─ 1_clean.pdf
│  ├─ 2_DoB_variant.pdf
│  ├─ 3_age_only.pdf
│  ├─ 4_scanned_skewed.pdf
│  └─ 5_missing_report.pdf
├─ requirements.txt     # Dependencies
└─ README.md            # Documentation
