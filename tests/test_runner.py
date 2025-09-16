import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import glob, json
from extractor import run_pipeline

def main():
    pdfs = sorted(glob.glob("sample_pdfs/*.pdf"))
    if not pdfs:
        print("No PDFs in sample_pdfs/. Run tests/make_samples.py first.")
        return

    passes = 0; total = 0
    for f in pdfs:
        total += 1
        with open(f, "rb") as fh:
            out = run_pipeline(fh.read())
        found = sum([1 if out.get("patientName") else 0,
                     1 if (out.get("dob") or out.get("age") is not None) else 0,
                     1 if out.get("reportType") else 0])
        ok = found >= 2
        passes += 1 if ok else 0
        print(f"== {os.path.basename(f)} == found={found} ok={ok}\n{json.dumps(out, indent=2)}\n")

    print(f"Summary: {passes}/{total} files met >= 2/3 fields.")

if __name__ == "__main__":
    main()
