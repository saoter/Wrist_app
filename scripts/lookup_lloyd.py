# scripts/lookup_lloyd.py

import pandas as pd
import os

def find_matching_row(vessel_name: str, vessel_number: str, lloyds_path: str = "data/LloydsCurrentOwnership 28-Apr-2025.xlsx") -> dict:
    # Normalize input
    vessel_name = vessel_name.strip().lower() if vessel_name else None
    vessel_number = str(vessel_number).strip() if vessel_number else None

    if not os.path.exists(lloyds_path):
        raise FileNotFoundError(f"Lloyds Excel file not found at: {lloyds_path}")

    df = pd.read_excel(lloyds_path)

    match = None

    for _, row in df.iterrows():
        imo = str(row.get("IMO No", "")).strip()
        name = str(row.get("Vessel Name", "")).strip().lower()

        match_by_number = vessel_number and imo == vessel_number
        match_by_name = vessel_name and name == vessel_name

        if match_by_number or match_by_name:
            match = row.to_dict()
            break

    return match

if __name__ == "__main__":
    # Example test
    result = find_matching_row("LSC Boat V", "8423154")
    if result:
        print("✅ Match found:\n", result)
    else:
        print("❌ No match found.")
