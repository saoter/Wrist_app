# scripts/lookup_customer.py

import pandas as pd
from pathlib import Path
from scripts.get_new_file import get_latest_file

CUSTOMER_SHEET_NAME = 0  

_cached_df = None

def _load_customer_db() -> pd.DataFrame:
    global _cached_df
    if _cached_df is None:
        latest_customer_file = get_latest_file("Wrist")
        if latest_customer_file is None or not latest_customer_file.exists():
            raise FileNotFoundError("No Wrist*.xlsx file found in /data")

        print(f"[INFO] Loading customer database from {latest_customer_file.name} into memory...")
        _cached_df = pd.read_excel(latest_customer_file, sheet_name=CUSTOMER_SHEET_NAME, dtype=str)
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
