
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
    "pl_table": (
        BASE_PATH / "data/processed/PL_TABLE_WITH_SUB_CATEGORY.csv"
    ),

    "price_list_table": (
        BASE_PATH / "data/processed/PRICE_LIST_TABLE_WITH_LPP.csv"
    ),

    "promotion_table": (
        BASE_PATH / "data/processed/PROMOTION_TABLE.csv"
    )
}


# --------------------------------------------------
# Function to load a table
# --------------------------------------------------

def load_table(
    table_name,
    file_path,
    columns,
    insert_sql,
    primary_key="SKU"
):

    print(f"Loading {table_name}...")
    print(f"File: {file_path}")

    # Check that file exists
    if not file_path.exists():
        print(f"ERROR: File not found: {file_path}")
        print()
        return

    try:
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
        df = df[columns].copy()

        # Standardize SKU values
        if "SKU" in df.columns:
            df["SKU"] = (
                df["SKU"]
                .astype("string")
                .str.strip()
                .str.upper()
            )

        # Remove rows with missing primary key
        if primary_key in df.columns:
            missing_key_rows = df[primary_key].isna().sum()

            if missing_key_rows > 0:
                print(
                    f"WARNING: Removing {missing_key_rows} rows "
                    f"with missing {primary_key}"
                )

                df = df.dropna(subset=[primary_key])

        # Remove duplicate primary keys
        if primary_key in df.columns:
            duplicate_count = df.duplicated(
                subset=[primary_key]
            ).sum()

            if duplicate_count > 0:
                print(
                    f"WARNING: Removing {duplicate_count} "
                    f"duplicate {primary_key} rows"
                )

                # Keep the last occurrence
                df = df.drop_duplicates(
                    subset=[primary_key],
                    keep="last"
                )

        # Replace NaN with None for MySQL
        df = df.astype(object).where(
            pd.notna(df),
            None
        )

        # Convert DataFrame to list of tuples
        records = list(
            df.itertuples(
                index=False,
                name=None
            )
        )

        if not records:
            print(f"WARNING: No records to insert into {table_name}")
            print()
            return

        # Insert records
        cursor.executemany(insert_sql, records)

        connection.commit()

        print(
            f"SUCCESS: {len(records)} rows processed "
            f"for {table_name}"
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
    ["PL", "SKU", "SUB_CATEGORY"],

    """
    INSERT INTO pl_table
    (PL, SKU, SUB_CATEGORY)

    VALUES (%s, %s, %s)

    ON DUPLICATE KEY UPDATE
        PL = VALUES(PL),
        SUB_CATEGORY = VALUES(SUB_CATEGORY)
    """
)


# --------------------------------------------------
# 2. PRICE LIST TABLE
# --------------------------------------------------

load_table(
    "price_list_table",
    files["price_list_table"],
    ["PL", "SKU", "MAP", "LPP"],

    """
    INSERT INTO price_list_table
    (PL, SKU, MAP, LPP)

    VALUES (%s, %s, %s, %s)

    ON DUPLICATE KEY UPDATE
        PL = VALUES(PL),
        MAP = VALUES(MAP),
        LPP = VALUES(LPP)
    """
)


# --------------------------------------------------
# 3. PROMOTION TABLE
# --------------------------------------------------

load_table(
    "promotion_table",
    files["promotion_table"],
    ["PL", "SKU", "Season", "Promotion"],

    """
    INSERT INTO promotion_table
    (PL, SKU, Season, Promotion)

    VALUES (%s, %s, %s, %s)

    ON DUPLICATE KEY UPDATE
        PL = VALUES(PL),
        Season = VALUES(Season),
        Promotion = VALUES(Promotion)
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