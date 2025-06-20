import pandas as pd
import os
from scripts.get_new_file import get_latest_file
from pathlib import Path

def find_matching_row(vessel_name: str, vessel_number: str) -> dict:
    # Get latest Lloyds file
    lloyds_path = get_latest_file("Lloyds")
    if lloyds_path is None or not lloyds_path.exists():
        raise FileNotFoundError("No Lloyds*.xlsx file found in /data")

    # Normalize input
    vessel_name = vessel_name.strip().lower() if vessel_name else None
    vessel_number = str(vessel_number).strip() if vessel_number else None

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
