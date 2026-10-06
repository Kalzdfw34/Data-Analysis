import pandas as pd
import mysql.connector
from pathlib import Path

# --------------------------------------------------
# MySQL connection
# --------------------------------------------------

connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Ahtirna*91",
    database="map_lpp_db"
)

cursor = connection.cursor()

print("Connected to MySQL successfully!")
print()


# --------------------------------------------------
# File locations
# --------------------------------------------------

BASE_PATH = Path(r"D:\Pro IT Bridge\MAP_LPP_Project")

files = {
    "pl_table": BASE_PATH / "data/converted/PL_TABLE.csv",

    "seller_mapping_table":
        BASE_PATH / "data/converted/SELLER_MAPPING_TABLE.csv",

    "price_list_table":
        BASE_PATH / "data/processed/PRICE_LIST_TABLE_WITH_LPP.csv",

    "category_mapping_table":
        BASE_PATH / "data/processed/CATEGORY_MAPPING_TABLE.csv",

    "promotion_table":
        BASE_PATH / "data/processed/PROMOTION_TABLE.csv"
}


# --------------------------------------------------
# Function to load a table
# --------------------------------------------------

def load_table(table_name, file_path, columns, insert_sql):

    print(f"Loading {table_name}...")
    print(f"File: {file_path}")

    # Check that file exists
    if not file_path.exists():
        print(f"ERROR: File not found: {file_path}")
        print()
        return

    # Read CSV
    df = pd.read_csv(file_path)

    print(f"CSV rows found: {len(df)}")
    print(f"CSV columns: {list(df.columns)}")

    # Check required columns
    missing_columns = [
        col for col in columns
        if col not in df.columns
    ]

    if missing_columns:
        print(f"ERROR: Missing columns: {missing_columns}")
        print()
        return

    # Keep only required columns and maintain correct order
    df = df[columns]

    # Replace NaN with None for MySQL
    df = df.where(pd.notnull(df), None)

    # Convert dataframe to list of tuples
    records = list(df.itertuples(index=False, name=None))

    try:

        cursor.executemany(insert_sql, records)

        connection.commit()

        print(
            f"SUCCESS: {cursor.rowcount} rows inserted into {table_name}"
        )

    except Exception as e:

        connection.rollback()

        print(f"ERROR loading {table_name}:")
        print(e)

    print()


# --------------------------------------------------
# 1. PL TABLE
# --------------------------------------------------

load_table(
    "pl_table",
    files["pl_table"],
    ["PL", "SKU", "SUB_CATEGORY", "CATEGORY"],

    """
    INSERT INTO pl_table
    (PL, SKU, SUB_CATEGORY, CATEGORY)
    VALUES (%s, %s, %s, %s)
    """
)


# --------------------------------------------------
# 2. SELLER MAPPING TABLE
# --------------------------------------------------

load_table(
    "seller_mapping_table",
    files["seller_mapping_table"],
    ["Seller_Name", "Homologated_Name"],

    """
    INSERT INTO seller_mapping_table
    (Seller_Name, Homologated_Name)
    VALUES (%s, %s)
    """
)


# --------------------------------------------------
# 3. PRICE LIST TABLE
# --------------------------------------------------

load_table(
    "price_list_table",
    files["price_list_table"],
    ["PL", "SKU", "MAP", "LPP"],

    """
    INSERT INTO price_list_table
    (PL, SKU, MAP, LPP)
    VALUES (%s, %s, %s, %s)
    """
)


# --------------------------------------------------
# 4. CATEGORY MAPPING TABLE
# --------------------------------------------------

load_table(
    "category_mapping_table",
    files["category_mapping_table"],
    ["Category", "sub_category", "PL", "SKU"],

    """
    INSERT INTO category_mapping_table
    (Category, sub_category, PL, SKU)
    VALUES (%s, %s, %s, %s)
    """
)


# --------------------------------------------------
# 5. PROMOTION TABLE
# --------------------------------------------------

load_table(
    "promotion_table",
    files["promotion_table"],
    ["PL", "SKU", "Season", "Promotion"],

    """
    INSERT INTO promotion_table
    (PL, SKU, Season, Promotion)
    VALUES (%s, %s, %s, %s)
    """
)


# --------------------------------------------------
# Close connection
# --------------------------------------------------

cursor.close()
connection.close()

print("====================================")
print("All remaining tables processed.")
print("MySQL connection closed.")
print("====================================")