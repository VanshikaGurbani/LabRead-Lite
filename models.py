from pydantic import BaseModel
from typing import Optional, List

class ExtractResponse(BaseModel):
    patientName: Optional[str]
    dob: Optional[str]
    age: Optional[int]
    reportType: Optional[str]
    gender: Optional[str] = None
    confidence: float
    warnings: List[str] = []
