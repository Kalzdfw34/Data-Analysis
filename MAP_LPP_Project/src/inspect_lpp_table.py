
from pathlib import Path
import pandas as pd


# Project paths
PROJECT_DIR = Path(__file__).resolve().parent.parent

LPP_FILE = PROJECT_DIR / "data" / "raw" / "LPP Calculations.xlsx"


# Read all sheets
sheets = pd.read_excel(LPP_FILE, sheet_name=None)


for sheet_name, df in sheets.items():

    print("\n" + "=" * 60)
    print(f"Sheet name: {sheet_name}")
    print("=" * 60)

    print("\nColumn names:")
    print(df.columns.tolist())

    print("\nFirst five rows:")
    print(df.head().to_string(index=False))