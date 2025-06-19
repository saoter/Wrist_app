# scripts/extract_from_pdf.py

import sys
import fitz  # PyMuPDF
import json
import requests
import pandas as pd
from pathlib import Path
from difflib import SequenceMatcher

# Ensure the parent directory is in sys.path to resolve 'scripts' properly
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.lookup_lloyd import find_matching_row
from scripts.lookup_customer import find_customer_entry

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "gemma3:latest"

PROMPT_TEMPLATE = """
You are a document analysis assistant.

Please analyze the following document and extract the required information to support the ABC-Invoice account model in accordance with Wrist procedures.

Extract the following details clearly:

A) "Billing counterpart" – Who is the *registered owner* of the vessel?

B) "Ordering party" – Who is *placing the order*? (Typically marked as "Care of" or "Plain")

C) "Special billing instructions" – Are there any billing-related notes or special handling instructions?

D) "Special postal address" – Is there a special postal address noted?

E) "Billing address full" – What is the *full billing address*, including street, PO box, city, ZIP, country? (e.g., shown in billing details or under 'Buyer details')

F) "Vessel name and number" – each document has vessel name and number.

Respond ONLY with a pure JSON object, with NO explanations or extra text. Do NOT include markdown or preamble.

If a value is not available, use the literal null (not the string "null").

Use this format:
{{
  "billing_counterpart": "Name of registered owner",
  "ordering_party": "Care of XYZ / Plain XYZ",
  "billing_instructions": "Text or null",
  "special_postal_address": null,
  "billing_address_full": "Full billing address string",
  "vessel_name": "LSC Boat V",
  "vessel_number": "8423154"
}}

Here is the document text:
{text}
"""

CUSTOMER_DB_PATH = Path("data/Wrist MDM Live Customers 24-Apr-25.xlsx")

def extract_text_from_pdf(file_path: Path) -> str:
    print(f"[INFO] Reading PDF: {file_path}")
    doc = fitz.open(file_path)
    return "\n".join(page.get_text() for page in doc)

def query_ollama(text: str) -> str:
    prompt = PROMPT_TEMPLATE.format(text=text)
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_ctx": 8192}
    }

    try:
        print("[INFO] Sending text to LLM for extraction...")
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        data = response.json()

        if "response" in data:
            return data["response"].strip()
        else:
            print("[ERROR] 'response' field missing in Ollama reply:")
            print(data)
            return ""
    except Exception as e:
        print(f"[ERROR] Failed to contact Ollama: {e}")
        return ""

def fuzzy_match(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()

def save_result_as_json(result: str, output_path: Path):
    try:
        cleaned = result.strip().lstrip("`json").rstrip("`").strip()
        parsed_raw = json.loads(cleaned)
        from_order = {k.replace(" ", "_"): v for k, v in parsed_raw.items()}
        data = {"from_order": from_order}

        # Lloyd’s match
        vessel_name = from_order.get("vessel_name")
        vessel_number = from_order.get("vessel_number")
        billing = from_order.get("billing_counterpart")

        if vessel_name and vessel_number:
            match = find_matching_row(vessel_name, vessel_number)
            if match:
                from_lloyd = {
                    k.replace(" ", "_"): str(v) if not isinstance(v, (str, int, float, type(None), bool)) else v
                    for k, v in match.items()
                }
                data["from_lloyd"] = from_lloyd
                print("[INFO] Updated extracted data with Lloyd's info.")

                manager = from_lloyd.get("Technincal_Manager_-_Care_of")
                if billing and manager:
                    if billing.strip().lower() == manager.strip().lower():
                        data.setdefault("match", {})["billing_vs_manager"] = True
                        print("[INFO] Billing counterpart matches technical manager.")
                    else:
                        data.setdefault("match", {}).update({
                            "billing_vs_manager": False,
                            "billing_counterpart": billing,
                            "technical_manager": manager
                        })
                        print("[WARNING] Billing counterpart does NOT match technical manager:")
                        print(f"  billing_counterpart: {billing}")
                        print(f"  technical_manager:   {manager}")

        # Customer DB match
        if billing:
            customer_match = find_customer_entry(billing)
            if customer_match:
                joint_address_parts = [
                    str(customer_match.get("AddressPOBox_Inv", "")),
                    str(customer_match.get("AddressCity_Inv", "")),
                    str(customer_match.get("AddressCounty_Inv", "")),
                    str(customer_match.get("AddressState_Inv", "")),
                    str(customer_match.get("AddressZIPCode_Inv", "")),
                    str(customer_match.get("AddressCountry_Inv", ""))
                ]
                joint_address = ", ".join([part for part in joint_address_parts if part.strip()])

                data["from_customer_db"] = {
                    "customer_code": customer_match.get("Code"),
                    "invoice_name": customer_match.get("NameInvoiceAddress"),
                    "invoice_careof": customer_match.get("AddressCareOf_Inv"),
                    "joint_address": joint_address
                }
                print("[INFO] Found customer entry in MDM database.")

                billing_address_full = from_order.get("billing_address_full")
                if billing_address_full:
                    score = fuzzy_match(billing_address_full.lower(), joint_address.lower())
                    data.setdefault("match", {})["billing_address_vs_customer_address"] = score >= 0.8

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        print(f"[INFO] Saved extracted data to: {output_path}")

        print("\n[INFO] Summary for processed document:")
        print(f"  → Billing Counterpart: {from_order.get('billing_counterpart')}")
        print(f"  → Vessel Name / Number: {vessel_name} / {vessel_number}")
        if data.get("match", {}).get("billing_vs_manager"):
            print("  ✅ Billing matches technical manager in Lloyd's")
        else:
            print("  ❌ Billing does NOT match technical manager")

        if "from_customer_db" in data:
            print("  🏷️  Customer Match (MDM DB):")
            print(f"     ↳ Code: {data['from_customer_db'].get('customer_code')}")
            print(f"     ↳ Invoice Name: {data['from_customer_db'].get('invoice_name')}")
            print(f"     ↳ Care Of: {data['from_customer_db'].get('invoice_careof')}")
            if "billing_address_vs_customer_address" in data.get("match", {}):
                match_status = data['match']['billing_address_vs_customer_address']
                print(f"     ↳ Address Match: {'✅' if match_status else '❌'}")
        else:
            print("  ℹ️  No customer match found")

        print("-" * 60)
        print(f"[INFO] ✔️  Process for file {output_path.stem}.pdf is finished. Waiting for new files...")

    except Exception as e:
        print(f"[ERROR] Failed to process and save JSON: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_from_pdf.py path_to_pdf")
        sys.exit(1)

    pdf_path = Path(sys.argv[1])
    text = extract_text_from_pdf(pdf_path)
    result = query_ollama(text)
    output_json = pdf_path.with_suffix(".json")
    save_result_as_json(result, output_json)
