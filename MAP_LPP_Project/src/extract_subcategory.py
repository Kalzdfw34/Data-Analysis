
from pathlib import Path
import pandas as pd


# 1. Define project paths
PROJECT_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = PROJECT_DIR / "data" / "converted" / "PL_TABLE.csv"
OUTPUT_DIR = PROJECT_DIR / "data" / "processed"

# Create output folder if it does not exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "PL_TABLE_WITH_SUB_CATEGORY.csv"


# 2. Read the PL table
df = pd.read_csv(INPUT_FILE)


# 3. Extract SUB_CATEGORY from the PL column
# Example:
# DELLDF_SUP_TON       -> TON
# DELL0X_PC_Laptop     -> Laptop

df["SUB_CATEGORY"] = df["PL"].str.split("_").str[-1]


# 4. Remove unnecessary spaces
df["SUB_CATEGORY"] = df["SUB_CATEGORY"].str.strip()


# 5. Display sample results
print("\nSample results:")
print(df[["PL", "SUB_CATEGORY"]].head(10).to_string(index=False))


# 6. Display unique subcategories
print("\nUnique SUB_CATEGORY values:")
print(df["SUB_CATEGORY"].unique())


# 7. Save the updated CSV
df.to_csv(OUTPUT_FILE, index=False)


print(f"\nUpdated file saved successfully at:")
print(OUTPUT_FILE)