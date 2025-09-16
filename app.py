from fastapi import FastAPI, UploadFile, File, HTTPException
from models import ExtractResponse
from extractor import run_pipeline

app = FastAPI(title="LabRead Lite")

@app.post("/extract", response_model=ExtractResponse)
async def extract(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Please upload a PDF.")
    pdf_bytes = await file.read()
    try:
        result = run_pipeline(pdf_bytes)
    except Exception as e:
        raise HTTPException(500, f"Extraction error: {e}")
    return ExtractResponse(**result)

@app.get("/")
def home():
    return {
        "service": "LabRead Lite",
        "status": "running",
        "try": {
            "docs": "/docs",
            "openapi": "/openapi.json",
            "extract": "POST /extract (upload a PDF)"
        }
    }


@app.get("/health")
def health():
    return {"ok": True}