# scripts/lookup_customer.py

import pandas as pd
from pathlib import Path

CUSTOMER_DB_PATH = Path("data/Wrist MDM Live Customers 24-Apr-25.xlsx")
CUSTOMER_SHEET_NAME = 0  # Or set explicitly to the sheet name if needed

_cached_df = None

def _load_customer_db() -> pd.DataFrame:
    global _cached_df
    if _cached_df is None:
        print("[INFO] Loading customer database into memory...")
        _cached_df = pd.read_excel(CUSTOMER_DB_PATH, sheet_name=CUSTOMER_SHEET_NAME, dtype=str)
        _cached_df.fillna("", inplace=True)
    return _cached_df

def find_customer_entry(billing_counterpart: str) -> dict | None:
    df = _load_customer_db()
    if billing_counterpart:
        matches = df[df["NameInvoiceAddress"].str.strip().str.lower() == billing_counterpart.strip().lower()]
        if not matches.empty:
            print(f"[DEBUG] Found {len(matches)} match(es) in customer DB for '{billing_counterpart}'")
            return matches.iloc[0].to_dict()
        else:
            print(f"[DEBUG] No exact match in customer DB for '{billing_counterpart}'")
    return None
