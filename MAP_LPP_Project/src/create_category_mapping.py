
from pathlib import Path
import pandas as pd


# ============================================================
# 1. DEFINE PROJECT PATHS
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parent.parent

CONVERTED_DIR = PROJECT_DIR / "data" / "converted"
PROCESSED_DIR = PROJECT_DIR / "data" / "processed"

PL_TABLE_FILE = CONVERTED_DIR / "PL_TABLE.csv"

OUTPUT_FILE = PROCESSED_DIR / "CATEGORY_MAPPING_TABLE.csv"


# ============================================================
# 2. CHECK WHETHER THE INPUT FILE EXISTS
# ============================================================

if not PL_TABLE_FILE.exists():
    raise FileNotFoundError(
        f"PL_TABLE.csv was not found at: {PL_TABLE_FILE}"
    )


# Create the processed folder if it does not exist
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 3. READ THE PL TABLE
# ============================================================

print("Reading PL_TABLE.csv...")

pl_df = pd.read_csv(PL_TABLE_FILE)

# Standardize column names
pl_df.columns = (
    pl_df.columns
    .str.strip()
    .str.upper()
)


print("\nColumns available in PL_TABLE:")
print(pl_df.columns.tolist())


# ============================================================
# 4. VALIDATE REQUIRED COLUMNS
# ============================================================

required_columns = ["PL", "SKU"]

missing_columns = [
    column
    for column in required_columns
    if column not in pl_df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required columns in PL_TABLE.csv: {missing_columns}"
    )


# ============================================================
# 5. CLEAN PL AND SKU VALUES
# ============================================================

pl_df["PL"] = pl_df["PL"].astype("string").str.strip()

pl_df["SKU"] = pl_df["SKU"].astype("string").str.strip()


# Remove rows where PL or SKU is missing
pl_df = pl_df.dropna(subset=["PL", "SKU"]).copy()

pl_df = pl_df[
    (pl_df["PL"] != "")
    & (pl_df["SKU"] != "")
].copy()


# ============================================================
# 6. EXTRACT CATEGORY AND SUB_CATEGORY FROM PL
# ============================================================

# Example:
# HP8H_PC_Laptop
#
# Split result:
# ["HP8H", "PC", "Laptop"]
#
# Category     = second-last segment = PC
# sub_category = last segment        = Laptop

pl_parts = pl_df["PL"].str.split("_")


# Check that each PL has at least three segments
invalid_pl_rows = pl_parts.str.len() < 3

if invalid_pl_rows.any():
    print("\nWARNING: The following PL values do not have enough segments:")

    print(
        pl_df.loc[invalid_pl_rows, "PL"]
        .drop_duplicates()
        .to_string(index=False)
    )

    raise ValueError(
        "Some PL values cannot be used to extract Category and sub_category."
    )


# Extract the second-last segment as Category
pl_df["CATEGORY"] = pl_parts.str[-2].str.strip()


# Extract the last segment as sub_category
pl_df["SUB_CATEGORY"] = pl_parts.str[-1].str.strip()


# ============================================================
# 7. CREATE THE CATEGORY MAPPING TABLE
# ============================================================

category_mapping_df = pl_df[
    [
        "CATEGORY",
        "SUB_CATEGORY",
        "PL",
        "SKU"
    ]
].copy()


# Rename columns to the required output format
category_mapping_df = category_mapping_df.rename(
    columns={
        "CATEGORY": "Category",
        "SUB_CATEGORY": "sub_category"
    }
)


# ============================================================
# 8. REMOVE DUPLICATE MAPPINGS
# ============================================================

category_mapping_df = category_mapping_df.drop_duplicates(
    subset=["Category", "sub_category", "PL", "SKU"]
).reset_index(drop=True)


# ============================================================
# 9. VALIDATE THE OUTPUT
# ============================================================

required_output_columns = [
    "Category",
    "sub_category",
    "PL",
    "SKU"
]

missing_output_columns = [
    column
    for column in required_output_columns
    if column not in category_mapping_df.columns
]

if missing_output_columns:
    raise ValueError(
        f"Missing output columns: {missing_output_columns}"
    )


# ============================================================
# 10. SAVE THE CATEGORY MAPPING TABLE
# ============================================================

category_mapping_df = category_mapping_df[
    required_output_columns
]

category_mapping_df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# 11. DISPLAY RESULTS
# ============================================================

print("\nCategory Mapping Table created successfully!")

print(f"\nOutput file: {OUTPUT_FILE}")

print(
    f"\nTotal records created: {len(category_mapping_df)}"
)

print("\nFirst 10 records:")

print(
    category_mapping_df.head(10).to_string(index=False)
)

print("\nFinal columns:")

print(category_mapping_df.columns.tolist())