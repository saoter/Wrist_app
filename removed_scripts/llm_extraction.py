# scripts/llm_extraction.py

import requests
import json

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

E) "Vessel name and number" - each document has vessel name and number

Respond ONLY with a pure JSON object, with NO explanations or extra text. Do NOT include markdown or preamble.

Use this format:
{{
  "billing_counterpart": "Name of registered owner",
  "ordering_party": "Care of XYZ / Plain XYZ",
  "billing_instructions": "Text or null",
  "special_postal_address": "Text or null",
  "vessel name": "LSC Boat V",
  "vessel number": "8423154"
}}

Here is the document text:
{text}
"""

def query_ollama(text: str) -> str:
    prompt = PROMPT_TEMPLATE.format(text=text)
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        return response.json()["response"].strip()
    except Exception as e:
        print(f"[ERROR] Failed to contact Ollama: {e}")
        return ""

if __name__ == "__main__":
    test_text = "Care of ABC Marine. Owner: Lloyd's Shipping Co. Vessel Name: LSC Boat V. IMO No: 8423154."
    print(query_ollama(test_text))



def extract_pdf_data_with_llm(text: str) -> dict:
    response = query_ollama(text)
    try:
        return json.loads(response)
    except Exception as e:
        print(f"[ERROR] Failed to parse JSON from Ollama response: {e}")
        return {}