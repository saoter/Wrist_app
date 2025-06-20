# 📄 Wrist Vessel Invoice Extractor

This is an automated document processing pipeline built for Wrist. It watches a folder for new incoming PDF invoices, extracts structured data using a local LLM (Gemma 3 via Ollama), enriches it with vessel and customer database info, and saves the result as JSON files.

---

## 🧠 What It Does

1. **Monitors** the `documents/` folder for new PDF files.
2. **Extracts** key invoice fields from scanned PDFs using an LLM prompt (via [Ollama](https://ollama.com/)).
3. **Enriches** the data with:
   - Lloyd's vessel registry data
   - Wrist MDM Customer database
4. **Compares** extracted vs. registered data (e.g. billing counterpart, billing address).
5. **Saves** structured results to `.json` and moves processed PDFs to `documents/processed/`.

---


## ⚙️ Requirements

- Python 3.10+
- [Ollama](https://ollama.com) running locally at `http://127.0.0.1:11434`
- Ollama model: `gemma3:latest`
- Packages:
   - PyMuPDF
   - requests
   - pandas
   - openpyxl

---

## 🚀 Installation

```bash
# 1. Clone the repo
git clone https://github.com/saoter/Wrist_app
cd Wrist_app

# 2. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

## 🧠 Ollama Setup

Make sure Ollama is installed and running locally:

```bash
ollama run gemma3
```

---

It must be accessible at http://127.0.0.1:11434. You can test it with a simple cURL call:


```bash
curl http://127.0.0.1:11434/api/tags
```

---

## ▶️ Usage

To start watching for PDFs and process them automatically:

```bash
python app.py
```

---

Drop a new PDF into documents/ — the app will:

   - Process it via LLM

   - Save .json output

   - Move the PDF to documents/processed/


