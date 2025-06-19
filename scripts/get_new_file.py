# scripts/get_new_file.py

import time
import subprocess
from pathlib import Path
import shutil

DOCUMENTS_DIR = Path("documents")
PROCESSED_DIR = DOCUMENTS_DIR / "processed"
PDF_EXTENSION = ".pdf"
EXTRACT_SCRIPT = Path("scripts/extract_from_pdf.py")

def find_latest_pdf(folder: Path) -> Path | None:
    """Returns the most recently added PDF file in the folder."""
    pdf_files = list(folder.glob(f"*{PDF_EXTENSION}"))
    if not pdf_files:
        return None
    return max(pdf_files, key=lambda f: f.stat().st_mtime)

def process_new_pdf(pdf_path: Path):
    """Calls the extract script with the PDF file."""
    print(f"[INFO] Processing file: {pdf_path.name}")
    subprocess.run(["python", str(EXTRACT_SCRIPT), str(pdf_path)], check=True)

    # Move to 'processed' folder after success
    PROCESSED_DIR.mkdir(exist_ok=True)
    dest = PROCESSED_DIR / pdf_path.name
    shutil.move(str(pdf_path), str(dest))
    print(f"[INFO] Moved processed file to: {dest}")

def get_new_pdf_path() -> Path | None:
    """Wrapper that handles detection and processing, returns extracted JSON path if new file found."""
    latest_pdf = find_latest_pdf(DOCUMENTS_DIR)
    if latest_pdf and latest_pdf.is_file():
        try:
            process_new_pdf(latest_pdf)
            return latest_pdf.with_suffix(".json")
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Failed to process {latest_pdf.name}: {e}")
    return None

if __name__ == "__main__":
    print("🚀 Watching for new PDFs in 'documents/'...")
    DOCUMENTS_DIR.mkdir(exist_ok=True)
    while True:
        get_new_pdf_path()
        time.sleep(3)
