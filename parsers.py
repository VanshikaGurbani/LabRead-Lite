import re
from datetime import datetime
from typing import Optional

DOB_KEYS = r"(?:DOB|DoB|D\.?O\.?B\.?|Date\s*of\s*Birth|Birth\s*Date)"
DATE_TOKEN = r"([0-9]{4}[-/][01]?\d[-/][0-3]?\d|[01]?\d[-/][0-3]?\d[-/][12]\d{3})"
AGE_PAT = re.compile(
    r"\bAge\b[\s:\-]*([0-9]{1,3})\b|([0-9]{1,3})\s*(?:yrs?|years?)\b",
    re.I,
)

NAME_RE = re.compile(
    r"^.*?\bPatient(?:\s*Name)?\b\s*[:\-]\s*"
    r"([A-Z][A-Za-z'\.\-]+(?:\s+[A-Z][A-Za-z'\.\-]+){1,3})\s*$",
    re.M,
)
GENDER_RE = re.compile(r"\b(?:Gender|Sex)\b\s*[:\-]\s*(Male|Female|M|F)\b", re.I)

REPORT_TOKENS = [
    "Comprehensive Metabolic Panel", "CMP",
    "Complete Blood Count", "CBC",
    "Lipid Panel",
    "HbA1c", "HBA1c", "HbAlc", "A1C", "A1c",
    "Thyroid Panel", "Thyroid Function",
    "Metabolic Panel", "Urinalysis",
]
REPORT_MAP = {
    "CMP": "Comprehensive Metabolic Panel",
    "CBC": "Complete Blood Count",
    "HBA1C": "HbA1c",
    "HBALC": "HbA1c",
    "A1C": "HbA1c",
    "A1c": "HbA1c",
}


#Parsers

def parse_name(text: str) -> Optional[str]:
    m = NAME_RE.search(text)
    return m.group(1).strip() if m else None


def _norm_date(s: str) -> Optional[str]:
    fmts = ["%Y-%m-%d", "%m/%d/%Y", "%d-%m-%Y", "%d/%m/%Y", "%m-%d-%Y", "%Y/%m/%d"]
    for f in fmts:
        try:
            return datetime.strptime(s, f).strftime("%Y-%m-%d")
        except Exception:
            continue
    return None


def parse_dob(text: str) -> Optional[str]:
    m = re.search(fr"{DOB_KEYS}\s*[:\-]?\s*{DATE_TOKEN}", text, re.I)
    return _norm_date(m.group(1)) if m else None


def parse_age(text: str) -> Optional[int]:
    m = AGE_PAT.search(text)
    if not m:
        m = re.search(r"Age\s*[\r\n]+\s*[:\-]?\s*([0-9]{1,3})", text, re.I)
        if not m:
            return None
        val = m.group(1)
    else:
        val = m.group(1) or m.group(2)
    try:
        return int(val)
    except Exception:
        return None

def parse_gender(text: str):
    m = GENDER_RE.search(text)
    if not m:
        return None
    val = m.group(1).strip().upper()
    return "male" if val in ("M", "MALE") else "female"

def _canon_report(token: str) -> str:
    return REPORT_MAP.get(token.upper(), token)


def parse_report_type(text: str) -> Optional[str]:
    m = re.search(r"(?:Report\s*Type|Panel|Profile|Test)\s*[:\-]\s*([^\r\n]+)", text, re.I)
    if m:
        token = m.group(1).strip()
        for w in re.findall(r"[A-Za-z0-9]+", token):
            canon = _canon_report(w)
            if canon != w:
                return canon
        return token

    pattern = r"\b(" + "|".join(re.escape(t) for t in REPORT_TOKENS) + r")\b"
    m = re.search(pattern, text, re.I)
    if m:
        return _canon_report(m.group(1))

    return None
