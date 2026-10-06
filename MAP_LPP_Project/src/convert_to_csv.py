
from pathlib import Path
import json
import xml.etree.ElementTree as ET

import pandas as pd
import yaml


# ==========================================================
# 1. PROJECT AND FOLDER PATHS
# ==========================================================

PROJECT_DIR = Path(__file__).resolve().parent.parent

RAW_DATA_DIR = PROJECT_DIR / "data" / "raw"

OUTPUT_DIR = PROJECT_DIR / "data" / "converted"

# Create the output folder if it does not exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ==========================================================
# 2. JSON CONVERSION
# ==========================================================

def convert_json_to_csv(file_path, output_dir):

    print(f"\nProcessing JSON: {file_path.name}")

    try:
        # Read the complete JSON file
        with open(file_path, "r", encoding="utf-8-sig") as file:
            content = file.read().strip()

        if not content:
            print("Skipped: Empty JSON file")
            return

        # Try normal JSON first (array or object)
        try:
            data = json.loads(content)

            if isinstance(data, list):
                df = pd.json_normalize(data)

            elif isinstance(data, dict):
                df = pd.json_normalize(data)

            else:
                print("Skipped: Unsupported JSON structure")
                return

        except json.JSONDecodeError:

            # If normal JSON fails, try JSON Lines / NDJSON
            records = []

            for line_number, line in enumerate(content.splitlines(), start=1):

                line = line.strip()

                if not line:
                    continue

                try:
                    records.append(json.loads(line))

                except json.JSONDecodeError as error:
                    print(
                        f"Invalid JSON on line {line_number}: {error}"
                    )

            if not records:
                print("Skipped: No valid JSON records found")
                return

            df = pd.json_normalize(records)

        # Create output filename
        output_file = output_dir / f"{file_path.stem}.csv"

        # Save as CSV
        df.to_csv(output_file, index=False, encoding="utf-8-sig")

        print(f"Saved: {output_file}")
        print(f"Rows: {len(df)}")
        print(f"Columns: {list(df.columns)}")

    except Exception as error:

        print(f"ERROR processing {file_path.name}: {error}")


# ==========================================================
# 3. YAML CONVERSION
# ==========================================================

def convert_yaml_to_csv(file_path, output_dir):

    print(f"\nProcessing YAML: {file_path.name}")

    try:

        with open(file_path, "r", encoding="utf-8-sig") as file:

            data = yaml.safe_load(file)

        if isinstance(data, list):

            df = pd.json_normalize(data)

        elif isinstance(data, dict):

            # Handle a dictionary containing records
            list_values = [
                value for value in data.values()
                if isinstance(value, list)
            ]

            if len(list_values) == 1:

                df = pd.json_normalize(list_values[0])

            else:

                df = pd.json_normalize(data)

        else:

            print("Skipped: Unsupported YAML structure")
            return

        output_file = output_dir / f"{file_path.stem}.csv"

        df.to_csv(output_file, index=False, encoding="utf-8-sig")

        print(f"Saved: {output_file}")
        print(f"Rows: {len(df)}")
        print(f"Columns: {list(df.columns)}")

    except Exception as error:

        print(f"ERROR processing {file_path.name}: {error}")


# ==========================================================
# 4. XML CONVERSION
# ==========================================================

def convert_xml_to_csv(file_path, output_dir):

    print(f"\nProcessing XML: {file_path.name}")

    try:

        tree = ET.parse(file_path)

        root = tree.getroot()

        records = []

        # Read child elements as records
        for item in root:

            record = {}

            # Read attributes, if present
            for key, value in item.attrib.items():

                record[key] = value

            # Read child elements
            for child in item:

                record[child.tag] = child.text

            if record:

                records.append(record)

        if not records:

            print("Skipped: No records found in XML")
            return

        df = pd.DataFrame(records)

        output_file = output_dir / f"{file_path.stem}.csv"

        df.to_csv(output_file, index=False, encoding="utf-8-sig")

        print(f"Saved: {output_file}")
        print(f"Rows: {len(df)}")
        print(f"Columns: {list(df.columns)}")

    except Exception as error:

        print(f"ERROR processing {file_path.name}: {error}")


# ==========================================================
# 5. EXCEL CONVERSION
# ==========================================================

def convert_excel_to_csv(file_path, output_dir):

    print(f"\nProcessing Excel: {file_path.name}")

    try:

        # Read all sheets
        sheets = pd.read_excel(
            file_path,
            sheet_name=None
        )

        for sheet_name, df in sheets.items():

            # Skip completely empty sheets
            if df.empty:

                print(f"Skipped empty sheet: {sheet_name}")
                continue

            # Create a safe sheet name for the output filename
            safe_sheet_name = str(sheet_name)

            output_file = (
                output_dir
                / f"{file_path.stem}_{safe_sheet_name}.csv"
            )

            df.to_csv(
                output_file,
                index=False,
                encoding="utf-8-sig"
            )

            print(f"Saved: {output_file}")
            print(f"Rows: {len(df)}")
            print(f"Columns: {list(df.columns)}")

    except Exception as error:

        print(f"ERROR processing {file_path.name}: {error}")


# ==========================================================
# 6. PROCESS ALL SOURCE FILES
# ==========================================================

def main():

    if not RAW_DATA_DIR.exists():

        print("ERROR: data/raw folder does not exist")

        return

    files = [
        file for file in RAW_DATA_DIR.rglob("*")
        if file.is_file()
    ]

    if not files:

        print("No source files found")

        return

    print("=" * 60)
    print("MAP LPP PROJECT - CSV CONVERSION")
    print("=" * 60)

    print(f"Input folder: {RAW_DATA_DIR}")
    print(f"Output folder: {OUTPUT_DIR}")
    print(f"Files found: {len(files)}")

    for file_path in sorted(files):

        extension = file_path.suffix.lower()

        if extension == ".json":

            convert_json_to_csv(
                file_path,
                OUTPUT_DIR
            )

        elif extension in [".yaml", ".yml"]:

            convert_yaml_to_csv(
                file_path,
                OUTPUT_DIR
            )

        elif extension == ".xml":

            convert_xml_to_csv(
                file_path,
                OUTPUT_DIR
            )

        elif extension in [".xlsx", ".xls"]:

            convert_excel_to_csv(
                file_path,
                OUTPUT_DIR
            )

        elif extension == ".csv":

            print(
                f"\nSkipped existing CSV: {file_path.name}"
            )

        else:

            print(
                f"\nSkipped unsupported file: {file_path.name}"
            )

    print("\n" + "=" * 60)
    print("CSV CONVERSION COMPLETED")
    print("=" * 60)


if __name__ == "__main__":

    main()