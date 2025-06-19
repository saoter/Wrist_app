# 📄 Wrist Vessel Invoice Extractor

This is an automated document processing pipeline built for Wrist. It watches a folder for new incoming PDF invoices, extracts structured data using a local LLM (Gemma 3 via Ollama), enriches it with vessel and customer database info, and saves the result as JSON files.

---

## 🧠 What It Does

1. **Monitors** the `documents/` folder for new PDF files.
2. **Extracts** key invoice fields from scanned PDFs using an LLM prompt (via [Ollama](https://ollama.com/)).
3. **Enriches** the data with:
   - Lloyd's vessel registry data (`scripts/lookup_lloyd.py`)
   - Wrist MDM Customer database (`data/Wrist MDM Live Customers 24-Apr-25.xlsx`)
4. **Compares** extracted vs. registered data (e.g. billing counterpart, billing address).
5. **Saves** structured results to `.json` and moves processed PDFs to `documents/processed/`.

---

## 🧱 Project Structure

project/
├── app.py # Watches folder and triggers processing

├── extract_from_pdf.py # Main logic: OCR → LLM → matching → JSON output

├── scripts/

│ ├── get_new_file.py # Detects new PDFs

│ ├── lookup_lloyd.py # Searches Lloyd’s vessel data

│ └── lookup_customer.py # Searches MDM customer data

├── data/

│ ├── vessel_db.csv # Lloyd’s vessel registry

│ └── Wrist MDM Live Customers 24-Apr-25.xlsx # Customer records

├── documents/

│ ├── [incoming PDFs]

│ └── processed/ # Processed PDFs moved here


## ⚙️ Requirements

- Python 3.10+
- [Ollama](https://ollama.com) running locally at `http://127.0.0.1:11434`
- Ollama model: `gemma3:latest`
- Packages:
  - `fitz` (via `PyMuPDF`)
  - `requests`
  - `pandas`
  - `openpyxl`

---

## 🚀 Installation

```bash
# 1. Clone the repo
git clone https://github.com/your-username/wrist-vessel-invoice-extractor.git
cd wrist-vessel-invoice-extractor

# 2. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

