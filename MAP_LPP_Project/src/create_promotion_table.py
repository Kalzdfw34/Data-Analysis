
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


# ============================================================
# 2. INPUT AND OUTPUT FILES
# ============================================================

PROMOTION_FILE = RAW_DIR / "PROMOTION_TABLE.xlsx"

PRICE_LIST_FILE = PROCESSED_DIR / "PRICE_LIST_TABLE_WITH_LPP.csv"

CATEGORY_MAPPING_FILE = PROCESSED_DIR / "CATEGORY_MAPPING_TABLE.csv"

OUTPUT_FILE = PROCESSED_DIR / "PROMOTION_TABLE.csv"


# ============================================================
# 3. CURRENT SEASON
# ============================================================

# September falls under Q4 (August–October)

CURRENT_SEASON = "Q4"


# ============================================================
# 4. CHECK INPUT FILES
# ============================================================

print("=" * 70)
print("CHECKING INPUT FILES")
print("=" * 70)


required_files = [
    PROMOTION_FILE,
    PRICE_LIST_FILE,
    CATEGORY_MAPPING_FILE
]


for file_path in required_files:

    if file_path.exists():

        print(f"FOUND: {file_path}")

    else:

        raise FileNotFoundError(
            f"\nRequired file is missing:\n{file_path}\n"
            "Please verify the file name and location."
        )


# ============================================================
# 5. READ PRICE LIST AND CATEGORY MAPPING TABLES
# ============================================================

print("\n" + "=" * 70)
print("READING PRICE LIST AND CATEGORY MAPPING TABLES")
print("=" * 70)


price_list_df = pd.read_csv(PRICE_LIST_FILE)

category_mapping_df = pd.read_csv(CATEGORY_MAPPING_FILE)


# Standardize column names
price_list_df.columns = (
    price_list_df.columns
    .str.strip()
    .str.upper()
)

category_mapping_df.columns = (
    category_mapping_df.columns
    .str.strip()
    .str.upper()
)


print("\nPrice List columns:")
print(price_list_df.columns.tolist())


print("\nCategory Mapping columns:")
print(category_mapping_df.columns.tolist())


# ============================================================
# 6. VALIDATE REQUIRED COLUMNS
# ============================================================

required_price_list_columns = [
    "PL",
    "SKU",
    "MAP"
]


required_category_columns = [
    "CATEGORY",
    "SUB_CATEGORY",
    "PL",
    "SKU"
]


for column in required_price_list_columns:

    if column not in price_list_df.columns:

        raise KeyError(
            f"Column '{column}' is missing from the Price List Table."
        )


for column in required_category_columns:

    if column not in category_mapping_df.columns:

        raise KeyError(
            f"Column '{column}' is missing from the Category Mapping Table."
        )


# ============================================================
# 7. STANDARDIZE JOIN COLUMNS
# ============================================================

print("\n" + "=" * 70)
print("STANDARDIZING JOIN COLUMNS")
print("=" * 70)


for dataframe in [
    price_list_df,
    category_mapping_df
]:

    dataframe["PL"] = (
        dataframe["PL"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    dataframe["SKU"] = (
        dataframe["SKU"]
        .astype(str)
        .str.strip()
        .str.upper()
    )


# ============================================================
# 8. STANDARDIZE CATEGORY AND SUBCATEGORY
# ============================================================

def standardize_category(value):

    """
    Standardize category names.

    Examples:
        Supply         -> SUP
        SUP             -> SUP
        Print Hardware -> PH
        PH              -> PH
        PC              -> PC
    """

    if pd.isna(value):

        return None

    value = str(value).strip().upper()

    category_mapping = {

        "SUPPLY": "SUP",
        "SUP": "SUP",

        "PRINT HARDWARE": "PH",
        "PRINT_HARDWARE": "PH",
        "PH": "PH",

        "PC": "PC"
    }

    return category_mapping.get(value, value)


def standardize_subcategory(value):

    """
    Standardize subcategory names.
    """

    if pd.isna(value):

        return None

    value = str(value).strip().upper()

    # Remove numbering such as:
    # 1. INK
    # 7. INK

    value = re.sub(
        r"^\s*\d+\s*[\.\-\)]\s*",
        "",
        value
    ).strip()

    subcategory_mapping = {

        "LJ": "LASERJET",
        "LASER JET": "LASERJET",
        "LASERJET": "LASERJET",

        "IJ": "INKJET",
        "INK JET": "INKJET",
        "INKJET": "INKJET",

        "INK": "INK",

        "TON": "TONER",
        "TONER": "TONER"
    }

    return subcategory_mapping.get(value, value)


category_mapping_df["CATEGORY_STANDARD"] = (
    category_mapping_df["CATEGORY"]
    .apply(standardize_category)
)


category_mapping_df["SUB_CATEGORY_STANDARD"] = (
    category_mapping_df["SUB_CATEGORY"]
    .apply(standardize_subcategory)
)


# ============================================================
# 9. CLEAN AND PREPARE PRICE LIST
# ============================================================

price_list_df["MAP"] = pd.to_numeric(
    price_list_df["MAP"],
    errors="coerce"
)


# Remove rows without a valid MAP
price_list_df = price_list_df[
    price_list_df["MAP"].notna()
].copy()


# ============================================================
# 10. MERGE CATEGORY MAPPING INTO PRICE LIST
# ============================================================

print("\n" + "=" * 70)
print("MERGING CATEGORY MAPPING INTO PRICE LIST")
print("=" * 70)


category_lookup = category_mapping_df[
    [
        "PL",
        "SKU",
        "CATEGORY_STANDARD",
        "SUB_CATEGORY_STANDARD"
    ]
].drop_duplicates(
    subset=["PL", "SKU"]
)


price_list_df = price_list_df.merge(
    category_lookup,
    on=["PL", "SKU"],
    how="left"
)


print("\nNumber of Price List records:")
print(len(price_list_df))


print("\nCategory counts:")

print(
    price_list_df["CATEGORY_STANDARD"]
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
# 11. READ PROMOTION WORKBOOK
# ============================================================

print("\n" + "=" * 70)
print("READING PROMOTION WORKBOOK")
print("=" * 70)


promotion_raw = pd.read_excel(
    PROMOTION_FILE,
    sheet_name=0,
    header=None
)


print("\nPromotion workbook preview:")

print(
    promotion_raw
    .head(20)
    .to_string(index=True, header=False)
)


# ============================================================
# 12. LOCATE THE OFFER TABLE
# ============================================================

print("\n" + "=" * 70)
print("LOCATING OFFER TABLE")
print("=" * 70)


offer_header_row = None


for row_index in range(len(promotion_raw)):

    row_values = (
        promotion_raw
        .iloc[row_index]
        .astype(str)
        .str.strip()
        .str.upper()
        .tolist()
    )

    row_text = " ".join(row_values)

    has_category = "CATEGORY" in row_values

    has_q4 = (
        "Q4 (AUG-OCT)" in row_text
        or "Q4(AUG-OCT)" in row_text
        or "Q4" in row_values
    )

    if has_category and has_q4:

        offer_header_row = row_index

        break


if offer_header_row is None:

    raise ValueError(
        "Could not find the Offer Table header in the "
        "Promotion workbook."
    )


print(
    f"Offer table header found at row index: {offer_header_row}"
)


# ============================================================
# 13. EXTRACT OFFER TABLE
# ============================================================

offer_header_values = (
    promotion_raw
    .iloc[offer_header_row]
    .astype(str)
    .str.strip()
    .tolist()
)


offer_header_values_upper = [
    value.upper()
    for value in offer_header_values
]


category_column_index = None
q4_column_index = None


for index, value in enumerate(offer_header_values_upper):

    if value == "CATEGORY":

        category_column_index = index

    if (
        value == "Q4 (AUG-OCT)"
        or value == "Q4(AUG-OCT)"
        or value == "Q4"
    ):

        q4_column_index = index


if category_column_index is None:

    raise ValueError(
        "Could not find the Category column in the Offer Table."
    )


if q4_column_index is None:

    raise ValueError(
        "Could not find the Q4 (Aug-Oct) column in the Offer Table."
    )


offer_table = promotion_raw.iloc[
    offer_header_row + 1:,
    [
        category_column_index,
        q4_column_index
    ]
].copy()


offer_table.columns = [
    "CATEGORY",
    "Q4_PROMOTION"
]


# Remove empty rows
offer_table = offer_table.dropna(
    subset=["CATEGORY", "Q4_PROMOTION"]
)


offer_table["CATEGORY_STANDARD"] = (
    offer_table["CATEGORY"]
    .apply(standardize_category)
)


offer_table["Q4_PROMOTION"] = (
    offer_table["Q4_PROMOTION"]
    .astype(str)
    .str.strip()
)


print("\nQ4 Offer Table:")

print(
    offer_table[
        [
            "CATEGORY",
            "CATEGORY_STANDARD",
            "Q4_PROMOTION"
        ]
    ].to_string(index=False)
)


# ============================================================
# 14. PARSE PROMOTION RULES
# ============================================================

def parse_promotion_rule(promotion_text):

    """
    Parse promotion text and return:

        Promotion type
        Percentage
        Fixed amount
        Subcategory restriction

    Examples:

        20% off ink
            -> PERCENTAGE, 0.20, None, INK

        $10 off laser jet
            -> FIXED, None, 10, LASERJET

        15 % off
            -> PERCENTAGE, 0.15, None, None
    """

    text = str(promotion_text).strip().upper()

    # Normalize spaces
    text = re.sub(r"\s+", " ", text)

    # Identify percentage discount
    percentage_match = re.search(
        r"(\d+(?:\.\d+)?)\s*%",
        text
    )

    # Identify fixed dollar discount
    fixed_amount_match = re.search(
        r"\$\s*(\d+(?:\.\d+)?)",
        text
    )

    # Remove discount portion to identify subcategory
    remaining_text = re.sub(
        r"\$\s*\d+(?:\.\d+)?",
        "",
        text
    )

    remaining_text = re.sub(
        r"\d+(?:\.\d+)?\s*%",
        "",
        remaining_text
    )

    remaining_text = re.sub(
        r"\bOFF\b",
        "",
        remaining_text
    ).strip()

    remaining_text = re.sub(
        r"\s+",
        " ",
        remaining_text
    ).strip()

    # Standardize the subcategory mentioned in the offer
    promotion_subcategory = None

    if remaining_text:

        promotion_subcategory = standardize_subcategory(
            remaining_text
        )

    # Percentage promotion
    if percentage_match:

        percentage_value = (
            float(percentage_match.group(1)) / 100
        )

        return {
            "PROMOTION_TYPE": "PERCENTAGE",
            "PERCENTAGE": percentage_value,
            "FIXED_AMOUNT": None,
            "PROMOTION_SUBCATEGORY": promotion_subcategory
        }

    # Fixed amount promotion
    if fixed_amount_match:

        fixed_amount = float(
            fixed_amount_match.group(1)
        )

        return {
            "PROMOTION_TYPE": "FIXED",
            "PERCENTAGE": None,
            "FIXED_AMOUNT": fixed_amount,
            "PROMOTION_SUBCATEGORY": promotion_subcategory
        }

    # Other promotion types such as:
    # Free accessories
    # Free setup service

    return {
        "PROMOTION_TYPE": "OTHER",
        "PERCENTAGE": None,
        "FIXED_AMOUNT": None,
        "PROMOTION_SUBCATEGORY": promotion_subcategory
    }


parsed_promotions = []


for _, row in offer_table.iterrows():

    parsed_rule = parse_promotion_rule(
        row["Q4_PROMOTION"]
    )

    parsed_promotions.append({

        "CATEGORY_STANDARD": row["CATEGORY_STANDARD"],

        "Q4_PROMOTION": row["Q4_PROMOTION"],

        **parsed_rule
    })


promotion_rules_df = pd.DataFrame(parsed_promotions)


print("\nParsed Q4 Promotion Rules:")

print(
    promotion_rules_df.to_string(index=False)
)


# ============================================================

# ============================================================
# 11A. EXTRACT PROMOTIONAL SKUS
# ============================================================

print("\n" + "=" * 70)
print("READING PROMOTIONAL SKUS")
print("=" * 70)

promotional_sku_header_row = None

for row_index in range(len(promotion_raw)):

    row_values = (
        promotion_raw
        .iloc[row_index]
        .astype(str)
        .str.strip()
        .str.upper()
        .tolist()
    )

    if "FOR THE SKU BELOW" in row_values:
        promotional_sku_header_row = row_index
        break

if promotional_sku_header_row is None:
    raise ValueError(
        "Could not find the 'For the SKU Below' header "
        "in the Promotion workbook."
    )

print(
    "Promotional SKU header found at row index:",
    promotional_sku_header_row
)

# The Promotional SKUs are listed in COLUMN B below
# 'For the SKU Below'.  The PL/SKU/Season/Promotion
# table starts in columns D:G, so it must NOT be treated
# as a stopping point for the SKU list.
promotional_sku_values = []

for row_index in range(promotional_sku_header_row + 1, len(promotion_raw)):

    value = str(promotion_raw.iloc[row_index, 1]).strip().upper()

    if value in {"", "NAN", "NONE"}:
        continue

    if value in {
        "PROMOTIONAL SKUS",
        "FOR THE SKU BELOW",
        "PL",
        "SKU",
        "SEASON",
        "PROMOTION"
    }:
        continue

    promotional_sku_values.append(value)

promotional_sku_set = set(promotional_sku_values)

print(
    "Number of Promotional SKUs found:",
    len(promotional_sku_set)
)

if len(promotional_sku_set) == 0:
    raise ValueError(
        "No Promotional SKUs were found after the "
        "'For the SKU Below' header."
    )

print("\nSample Promotional SKUs:")
print(list(sorted(promotional_sku_set))[:10])

# 15. APPLY PROMOTION RULES TO PRICE LIST
# ============================================================

print("\n" + "=" * 70)
print("APPLYING Q4 PROMOTIONS")
print("=" * 70)


def calculate_promotion(row):

    sku = row["SKU"]
    category = row["CATEGORY_STANDARD"]
    subcategory = row["SUB_CATEGORY_STANDARD"]
    map_value = row["MAP"]

    # Step 1: Only the SKUs listed in the Promotional SKUs
    # section are eligible for a promotion.
    if sku not in promotional_sku_set:
        return 0.0

    # Step 2: Find the Q4 promotion rule for the category.
    matching_rules = promotion_rules_df[
        promotion_rules_df["CATEGORY_STANDARD"] == category
    ]

    if matching_rules.empty:
        return 0.0

    # Step 3: Match the subcategory and calculate the discount.
    for _, rule in matching_rules.iterrows():

        promotion_subcategory = rule["PROMOTION_SUBCATEGORY"]

        if (
            pd.notna(promotion_subcategory)
            and promotion_subcategory != subcategory
        ):
            continue

        if rule["PROMOTION_TYPE"] == "PERCENTAGE":

            percentage = rule["PERCENTAGE"]

            return round(map_value * percentage, 2)

        elif rule["PROMOTION_TYPE"] == "FIXED":

            fixed_amount = rule["FIXED_AMOUNT"]

            return round(fixed_amount, 2)

        elif rule["PROMOTION_TYPE"] == "OTHER":

            return 0.0

    return 0.0


price_list_df["PROMOTION"] = (
    price_list_df.apply(
        calculate_promotion,
        axis=1
    )
)

# 16. ASSIGN SEASON
# ============================================================

price_list_df["SEASON"] = CURRENT_SEASON


# ============================================================
# 17. DISPLAY PROMOTION RESULTS
# ============================================================

print("\n" + "=" * 70)
print("PROMOTION CALCULATION RESULTS")
print("=" * 70)


print(
    price_list_df[
        [
            "PL",
            "SKU",
            "CATEGORY_STANDARD",
            "SUB_CATEGORY_STANDARD",
            "MAP",
            "SEASON",
            "PROMOTION"
        ]
    ]
    .head(30)
    .to_string(index=False)
)


# ============================================================
# 18. CHECK PROMOTIONAL SKU COVERAGE
# ============================================================

print("\n" + "=" * 70)
print("PROMOTIONAL SKU COVERAGE CHECK")
print("=" * 70)


# Check whether each price-list SKU exists
# in the Promotional SKU list.

price_list_df["PROMOTIONAL_SKU_ELIGIBLE"] = (
    price_list_df["SKU"].isin(promotional_sku_set)
)


print("\nTotal Promotional SKUs in workbook:")

print(
    len(promotional_sku_set)
)


print("\nMatching Promotional SKUs in Price List:")

print(
    price_list_df["PROMOTIONAL_SKU_ELIGIBLE"].sum()
)


print("\nProducts with a calculated promotion:")

print(
    (price_list_df["PROMOTION"] > 0).sum()
)


print("\nProducts without a promotion:")

print(
    (price_list_df["PROMOTION"] == 0).sum()
)


# Promotional SKUs that are not found in the Price List
price_list_skus = set(
    price_list_df["SKU"]
)


missing_promotional_skus = (
    promotional_sku_set - price_list_skus
)


print("\nPromotional SKUs missing from Price List:")

print(
    len(missing_promotional_skus)
)


if missing_promotional_skus:

    print("\nMissing Promotional SKU values:")

    print(
        sorted(missing_promotional_skus)
    )
# ============================================================
# 19. CREATE FINAL PROMOTION TABLE
# ============================================================

# Select the required columns
final_promotion_df = price_list_df[
    ["PL", "SKU", "SEASON", "PROMOTION"]
].copy()

# Rename only the required columns
final_promotion_df = final_promotion_df.rename(
    columns={
        "SEASON": "Season",
        "PROMOTION": "Promotion"
    }
)

# Arrange the columns in the required order
final_promotion_df = final_promotion_df[
    ["PL", "SKU", "Season", "Promotion"]
]

# Reorder columns exactly as requested
final_promotion_df = final_promotion_df[
    [
        "PL",
        "SKU",
        "Season",
        "Promotion"
    ]
]


# ============================================================
# 20. SAVE FINAL PROMOTION TABLE
# ============================================================

final_promotion_df.to_csv(
    OUTPUT_FILE,
    index=False
)


print("\n" + "=" * 70)
print("PROMOTION TABLE CREATED SUCCESSFULLY")
print("=" * 70)


print("\nFinal columns:")

print(
    final_promotion_df.columns.tolist()
)


print("\nSample final output:")

print(
    final_promotion_df
    .head(10)
    .to_string(index=False)
)


print("\nTotal records:")

print(
    len(final_promotion_df)
)


print("\nFile saved at:")

print(OUTPUT_FILE)

promotion_raw = pd.read_excel(
    PROMOTION_FILE,
    sheet_name=0,
    header=None
)

# ============================================================
