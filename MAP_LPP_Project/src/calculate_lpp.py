
from pathlib import Path
import pandas as pd
import re


# ============================================================
# 1. PROJECT PATHS
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = PROJECT_DIR / "data" / "raw"
CONVERTED_DIR = PROJECT_DIR / "data" / "converted"
PROCESSED_DIR = PROJECT_DIR / "data" / "processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# Input files
PL_FILE = CONVERTED_DIR / "PL_TABLE.csv"
PRICE_LIST_FILE = CONVERTED_DIR / "PRICE_LIST_TABLE.csv"
LPP_FILE = RAW_DIR / "LPP Calculations.xlsx"

# Output file
OUTPUT_FILE = PROCESSED_DIR / "PRICE_LIST_TABLE_WITH_LPP.csv"


# ============================================================
# 2. SUBCATEGORY STANDARDIZATION FUNCTION
# ============================================================

def standardize_subcategory(value):
    """
    Standardize subcategory names so that values from the
    PL table and LPP Calculation workbook can match.

    Examples:
        Laptop       -> LAPTOP
        1. Laptop    -> LAPTOP
        TON          -> TONER
        3. Toner     -> TONER
        LJ           -> LASERJET
        IJ           -> INKJET
        Ink          -> INK
        7. Ink       -> INK
    """

    if pd.isna(value):
        return None

    value = str(value).strip().upper()

    # Remove numbering and separators.
    #
    # Examples:
    # 1. LAPTOP  -> LAPTOP
    # 2) MONITOR -> MONITOR
    # 7. INK     -> INK

    value = re.sub(
        r"^\s*\d+\s*[\.\-\)]\s*",
        "",
        value
    ).strip()

    # Standardize alternate subcategory names
    subcategory_mapping = {

        # Toner
        "TON": "TONER",
        "TONER": "TONER",

        # Laserjet
        "LJ": "LASERJET",
        "LASER JET": "LASERJET",
        "LASERJET": "LASERJET",

        # Inkjet
        "IJ": "INKJET",
        "INK JET": "INKJET",
        "INKJET": "INKJET",

        # Ink
        "INK": "INK",

        # Other subcategories
        "LAPTOP": "LAPTOP",
        "MONITOR": "MONITOR",
        "DESKTOP": "DESKTOP"
    }

    return subcategory_mapping.get(value, value)


# ============================================================
# 3. CHECK WHETHER INPUT FILES EXIST
# ============================================================

print("=" * 70)
print("CHECKING INPUT FILES")
print("=" * 70)

required_files = [
    PL_FILE,
    PRICE_LIST_FILE,
    LPP_FILE
]

for file_path in required_files:

    if file_path.exists():

        print(f"FOUND: {file_path}")

    else:

        print(f"NOT FOUND: {file_path}")

        raise FileNotFoundError(
            f"\nRequired file is missing:\n{file_path}\n"
            "Please verify the file name and location."
        )


# ============================================================
# 4. READ PL TABLE AND PRICE LIST TABLE
# ============================================================

print("\n" + "=" * 70)
print("READING INPUT CSV FILES")
print("=" * 70)

pl_df = pd.read_csv(PL_FILE)

price_list_df = pd.read_csv(PRICE_LIST_FILE)


# Standardize column names
pl_df.columns = (
    pl_df.columns
    .str.strip()
    .str.upper()
)

price_list_df.columns = (
    price_list_df.columns
    .str.strip()
    .str.upper()
)


print("\nPL Table columns:")
print(pl_df.columns.tolist())

print("\nPrice List Table columns:")
print(price_list_df.columns.tolist())


# ============================================================
# 5. VALIDATE REQUIRED COLUMNS
# ============================================================

required_pl_columns = ["PL", "SKU"]

for column in required_pl_columns:

    if column not in pl_df.columns:

        raise KeyError(
            f"Column '{column}' is missing from PL_TABLE.csv."
        )


required_price_list_columns = ["PL", "SKU", "MAP"]

for column in required_price_list_columns:

    if column not in price_list_df.columns:

        raise KeyError(
            f"Column '{column}' is missing from PRICE_LIST_TABLE.csv."
        )


# ============================================================
# 6. EXTRACT SUB_CATEGORY FROM PL
# ============================================================

print("\n" + "=" * 70)
print("EXTRACTING SUB_CATEGORY")
print("=" * 70)


# Examples:
#
# HP8H_PC_Laptop        -> Laptop
# DELL0X_PC_Laptop      -> Laptop
# DELLDF_SUP_TON        -> TON
# HP8H_PC_LJ            -> LJ
# HP8H_PC_IJ            -> IJ
# HP8H_PC_Ink           -> Ink
#
# The final segment after the last underscore is extracted.

pl_df["SUB_CATEGORY"] = (
    pl_df["PL"]
    .astype(str)
    .str.strip()
    .str.split("_")
    .str[-1]
)


# ============================================================
# 7. EXTRACT BRAND FROM PL
# ============================================================

print("\n" + "=" * 70)
print("EXTRACTING BRAND")
print("=" * 70)


def extract_brand(pl_value):

    """
    Extract brand from the beginning of the PL value.

    Examples:
        HP8H_PC_Laptop    -> HP
        DELL0X_PC_Laptop  -> DELL
        DELLDF_SUP_TON    -> DELL
    """

    pl_value = str(pl_value).strip().upper()

    if pl_value.startswith("HP"):

        return "HP"

    elif pl_value.startswith("DELL"):

        return "DELL"

    else:

        return "UNKNOWN"


pl_df["BRAND"] = pl_df["PL"].apply(extract_brand)


# ============================================================
# 8. STANDARDIZE SUB_CATEGORY VALUES
# ============================================================

print("\n" + "=" * 70)
print("STANDARDIZING SUB_CATEGORY VALUES")
print("=" * 70)


pl_df["SUB_CATEGORY_STANDARD"] = (
    pl_df["SUB_CATEGORY"]
    .apply(standardize_subcategory)
)


# Display sample PL details
print("\nSample extracted PL details:")

print(
    pl_df[
        [
            "PL",
            "SKU",
            "SUB_CATEGORY",
            "SUB_CATEGORY_STANDARD",
            "BRAND"
        ]
    ]
    .head(20)
    .to_string(index=False)
)


# ============================================================
# 9. CREATE PL LOOKUP TABLE
# ============================================================

pl_lookup = pl_df[
    [
        "PL",
        "SKU",
        "SUB_CATEGORY",
        "SUB_CATEGORY_STANDARD",
        "BRAND"
    ]
].drop_duplicates()


# Remove any existing derived columns from the Price List Table
# to prevent duplicate columns when the script is run again.

columns_to_remove = [
    "SUB_CATEGORY",
    "SUB_CATEGORY_STANDARD",
    "BRAND"
]

price_list_df = price_list_df.drop(
    columns=[
        column
        for column in columns_to_remove
        if column in price_list_df.columns
    ]
)


# ============================================================
# 10. MERGE PL DETAILS INTO PRICE LIST TABLE
# ============================================================

print("\n" + "=" * 70)
print("MERGING PL DETAILS INTO PRICE LIST TABLE")
print("=" * 70)


# Convert join columns to strings and remove spaces
for dataframe in [pl_lookup, price_list_df]:

    dataframe["PL"] = (
        dataframe["PL"]
        .astype(str)
        .str.strip()
    )

    dataframe["SKU"] = (
        dataframe["SKU"]
        .astype(str)
        .str.strip()
    )


price_list_df = price_list_df.merge(
    pl_lookup,
    on=["PL", "SKU"],
    how="left"
)


print("\nNumber of Price List records:")
print(len(price_list_df))

print("\nBrand counts:")
print(
    price_list_df["BRAND"]
    .value_counts(dropna=False)
    .to_string()
)

print("\nSubcategory counts:")
print(
    price_list_df["SUB_CATEGORY_STANDARD"]
    .value_counts(dropna=False)
    .to_string()
)


# ============================================================
# 11. READ LPP CALCULATION WORKBOOK
# ============================================================

print("\n" + "=" * 70)
print("READING LPP CALCULATION WORKBOOK")
print("=" * 70)


# Read the workbook without assuming the header is on row 1.
# This is useful because the workbook contains title rows
# and blank rows before the LPP calculation table.

lpp_raw = pd.read_excel(
    LPP_FILE,
    sheet_name=0,
    header=None
)


print("\nRaw LPP workbook preview:")

print(
    lpp_raw
    .head(25)
    .to_string(index=True, header=False)
)


# ============================================================
# 12. LOCATE THE LPP TABLE HEADER AUTOMATICALLY
# ============================================================

print("\n" + "=" * 70)
print("LOCATING LPP TABLE HEADER")
print("=" * 70)


header_row_index = None


for row_index in range(len(lpp_raw)):

    row_values = (
        lpp_raw.iloc[row_index]
        .astype(str)
        .str.strip()
        .str.upper()
        .tolist()
    )

    row_text = " ".join(row_values)

    has_subcategory = (
        "SUB_CATEGORY" in row_text
        or "SUB CATEGORY" in row_text
        or "SUBCATEGORY" in row_text
    )

    has_hp = "HP" in row_values

    has_dell = (
        "DELL" in row_values
        or "DELL LPP%" in row_values
    )

    if has_subcategory and has_hp and has_dell:

        header_row_index = row_index

        break


if header_row_index is None:

    raise ValueError(
        "\nCould not automatically find the LPP table header.\n"
        "Please inspect the printed workbook preview and verify "
        "the subcategory, HP, and Dell header names."
    )


print(
    f"LPP header found at row index: {header_row_index}"
)


# ============================================================
# 13. EXTRACT LPP TABLE COLUMNS
# ============================================================

header_values = (
    lpp_raw.iloc[header_row_index]
    .astype(str)
    .str.strip()
    .str.upper()
    .tolist()
)


def find_column_index(possible_names):

    """
    Find a column index using possible column names.
    """

    for index, value in enumerate(header_values):

        if value in possible_names:

            return index

    return None


subcategory_column_index = find_column_index(
    [
        "SUB_CATEGORY",
        "SUB CATEGORY",
        "SUBCATEGORY"
    ]
)


hp_column_index = find_column_index(
    [
        "HP",
        "HP LPP%",
        "HP LPP %",
        "HP_LPP_PERCENTAGE"
    ]
)


dell_column_index = find_column_index(
    [
        "DELL",
        "DELL LPP%",
        "DELL LPP %",
        "DELL_LPP_PERCENTAGE"
    ]
)


if subcategory_column_index is None:

    raise ValueError(
        "Could not find the SUB_CATEGORY column "
        "in the LPP Calculation Table."
    )


if hp_column_index is None:

    raise ValueError(
        "Could not find the HP column "
        "in the LPP Calculation Table."
    )


if dell_column_index is None:

    raise ValueError(
        "Could not find the DELL column "
        "in the LPP Calculation Table."
    )


# Extract all rows below the header
lpp_table = lpp_raw.iloc[
    header_row_index + 1:,
    [
        subcategory_column_index,
        hp_column_index,
        dell_column_index
    ]
].copy()


# Assign standard column names
lpp_table.columns = [
    "SUB_CATEGORY",
    "HP_LPP_PERCENTAGE",
    "DELL_LPP_PERCENTAGE"
]


# ============================================================
# 14. CLEAN THE LPP TABLE
# ============================================================

print("\n" + "=" * 70)
print("CLEANING LPP CALCULATION TABLE")
print("=" * 70)


# Remove completely empty rows
lpp_table = lpp_table.dropna(
    how="all"
)


# Standardize subcategory values
lpp_table["SUB_CATEGORY_STANDARD"] = (
    lpp_table["SUB_CATEGORY"]
    .apply(standardize_subcategory)
)


# Convert percentages to numeric values
lpp_table["HP_LPP_PERCENTAGE"] = pd.to_numeric(
    lpp_table["HP_LPP_PERCENTAGE"],
    errors="coerce"
)

lpp_table["DELL_LPP_PERCENTAGE"] = pd.to_numeric(
    lpp_table["DELL_LPP_PERCENTAGE"],
    errors="coerce"
)


# Keep only rows with a valid subcategory
lpp_table = lpp_table[
    lpp_table["SUB_CATEGORY_STANDARD"].notna()
]


print("\nCleaned LPP table:")

print(
    lpp_table[
        [
            "SUB_CATEGORY",
            "SUB_CATEGORY_STANDARD",
            "HP_LPP_PERCENTAGE",
            "DELL_LPP_PERCENTAGE"
        ]
    ].to_string(index=False)
)


# ============================================================
# 15. CONVERT LPP TABLE FROM WIDE TO LONG FORMAT
# ============================================================

print("\n" + "=" * 70)
print("PREPARING LPP LOOKUP TABLE")
print("=" * 70)


# Original format:
#
# SUB_CATEGORY | HP | DELL
#
# Converted format:
#
# SUB_CATEGORY | BRAND | LPP_PERCENTAGE

lpp_long = lpp_table.melt(
    id_vars=[
        "SUB_CATEGORY",
        "SUB_CATEGORY_STANDARD"
    ],
    value_vars=[
        "HP_LPP_PERCENTAGE",
        "DELL_LPP_PERCENTAGE"
    ],
    var_name="BRAND_COLUMN",
    value_name="LPP_PERCENTAGE"
)


# Extract the brand from the column name
lpp_long["BRAND"] = (
    lpp_long["BRAND_COLUMN"]
    .str.replace(
        "_LPP_PERCENTAGE",
        "",
        regex=False
    )
    .str.upper()
)


# Remove any invalid or empty percentages
lpp_long = lpp_long[
    lpp_long["LPP_PERCENTAGE"].notna()
]


print("\nLPP lookup table:")

print(
    lpp_long[
        [
            "BRAND",
            "SUB_CATEGORY_STANDARD",
            "LPP_PERCENTAGE"
        ]
    ].to_string(index=False)
)


# ============================================================
# 16. MERGE LPP PERCENTAGE INTO PRICE LIST TABLE
# ============================================================

print("\n" + "=" * 70)
print("MATCHING BRAND AND SUB_CATEGORY")
print("=" * 70)


# Ensure the matching columns have consistent formats
price_list_df["BRAND"] = (
    price_list_df["BRAND"]
    .astype(str)
    .str.strip()
    .str.upper()
)

price_list_df["SUB_CATEGORY_STANDARD"] = (
    price_list_df["SUB_CATEGORY_STANDARD"]
    .apply(standardize_subcategory)
)


lpp_long["BRAND"] = (
    lpp_long["BRAND"]
    .astype(str)
    .str.strip()
    .str.upper()
)

lpp_long["SUB_CATEGORY_STANDARD"] = (
    lpp_long["SUB_CATEGORY_STANDARD"]
    .apply(standardize_subcategory)
)


# Check whether the LPP lookup contains duplicate keys
duplicate_keys = lpp_long[
    lpp_long.duplicated(
        subset=[
            "BRAND",
            "SUB_CATEGORY_STANDARD"
        ],
        keep=False
    )
]


if not duplicate_keys.empty:

    print("\nWARNING: Duplicate LPP lookup keys found:")

    print(
        duplicate_keys[
            [
                "BRAND",
                "SUB_CATEGORY_STANDARD",
                "LPP_PERCENTAGE"
            ]
        ].to_string(index=False)
    )


# Keep one row per brand and subcategory
lpp_lookup = lpp_long[
    [
        "BRAND",
        "SUB_CATEGORY_STANDARD",
        "LPP_PERCENTAGE"
    ]
].drop_duplicates(
    subset=[
        "BRAND",
        "SUB_CATEGORY_STANDARD"
    ]
)


# Merge LPP percentages
price_list_df = price_list_df.merge(
    lpp_lookup,
    on=[
        "BRAND",
        "SUB_CATEGORY_STANDARD"
    ],
    how="left"
)


# ============================================================
# 17. DISPLAY MATCHING RESULTS
# ============================================================

print("\n" + "=" * 70)
print("LPP MATCHING RESULTS")
print("=" * 70)


print(
    price_list_df[
        [
            "PL",
            "SKU",
            "BRAND",
            "SUB_CATEGORY",
            "SUB_CATEGORY_STANDARD",
            "LPP_PERCENTAGE"
        ]
    ]
    .head(20)
    .to_string(index=False)
)


# ============================================================
# 18. CONVERT MAP TO NUMERIC
# ============================================================

print("\n" + "=" * 70)
print("CALCULATING LPP")
print("=" * 70)


price_list_df["MAP"] = pd.to_numeric(
    price_list_df["MAP"],
    errors="coerce"
)


# ============================================================
# 19. CALCULATE REDUCTION AND LPP
# ============================================================

# Important:
#
# The LPP workbook uses decimal percentages.
#
# Example:
# LPP_PERCENTAGE = 0.034
# MAP = 10000
#
# REDUCTION = 10000 * 0.034 = 340
# LPP = 10000 - 340 = 9660
#
# Do NOT divide LPP_PERCENTAGE by 100 again.

price_list_df["REDUCTION"] = (
    price_list_df["MAP"]
    * price_list_df["LPP_PERCENTAGE"]
)


price_list_df["LPP"] = (
    price_list_df["MAP"]
    - price_list_df["REDUCTION"]
)


# Round the calculated monetary values
price_list_df["REDUCTION"] = (
    price_list_df["REDUCTION"]
    .round(2)
)

price_list_df["LPP"] = (
    price_list_df["LPP"]
    .round(2)
)


# ============================================================
# 20. CHECK FOR MISSING LPP PERCENTAGES
# ============================================================

print("\n" + "=" * 70)
print("CHECKING FOR MISSING LPP PERCENTAGES")
print("=" * 70)


missing_lpp = price_list_df[
    price_list_df["LPP_PERCENTAGE"].isna()
]


print("\nNumber of records missing LPP percentage:")
print(len(missing_lpp))


if not missing_lpp.empty:

    print("\nRecords missing LPP percentage:")

    print(
        missing_lpp[
            [
                "PL",
                "SKU",
                "BRAND",
                "SUB_CATEGORY",
                "SUB_CATEGORY_STANDARD"
            ]
        ]
        .drop_duplicates()
        .head(50)
        .to_string(index=False)
    )


# ============================================================
# 21. DISPLAY FINAL CALCULATION RESULTS
# ============================================================

print("\n" + "=" * 70)
print("FINAL LPP CALCULATION RESULTS")
print("=" * 70)


print(
    price_list_df[
        [
            "PL",
            "SKU",
            "BRAND",
            "SUB_CATEGORY",
            "MAP",
            "LPP_PERCENTAGE",
            "REDUCTION",
            "LPP"
        ]
    ]
    .head(30)
    .to_string(index=False)
)


# ============================================================
# 22. CREATE FINAL PRICE LIST TABLE
# ============================================================

# Keep only the required columns in the final output.

final_price_list_df = price_list_df[
    [
        "PL",
        "SKU",
        "MAP",
        "LPP"
    ]
].copy()


# Save the final Price List Table
final_price_list_df.to_csv(
    OUTPUT_FILE,
    index=False
)


print("\n" + "=" * 70)
print("FINAL PRICE LIST TABLE CREATED")
print("=" * 70)


print("\nFinal columns:")
print(final_price_list_df.columns.tolist())


print("\nSample final output:")

print(
    final_price_list_df
    .head(10)
    .to_string(index=False)
)


print("\nTotal records:")
print(len(final_price_list_df))


print("\nFile saved at:")
print(OUTPUT_FILE)
