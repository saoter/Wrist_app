# app.py

import json
from pathlib import Path
from scripts.get_new_file import get_new_pdf_path

def load_extracted_json(json_path: Path) -> dict:
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to load JSON from {json_path}: {e}")
        return {}

def main():
    print("🚀 Watching for new PDFs in 'documents/'...")

    while True:
        json_path = get_new_pdf_path()
        if json_path and json_path.exists():
            _ = load_extracted_json(json_path)
            # No further printing here, it's handled in extract_from_pdf.py

if __name__ == "__main__":
    main()
