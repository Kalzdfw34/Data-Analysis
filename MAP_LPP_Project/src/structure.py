import json
import yaml
import xml.etree.ElementTree as ET
from pathlib import Path
import openpyxl

PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_DIR / "data" / "raw"

def inspect_json(path):
    with open(path, "r", encoding="utf-8") as f:
        try:
            f.seek(0)
            data = json.load(f)
            fmt = "single JSON document"
        except json.JSONDecodeError:
            f.seek(0)
            data = [json.loads(line) for line in f if line.strip()]
            fmt = "JSON Lines (NDJSON)"
    print(f"  Format: {fmt}")
    print(f"  Top-level type: {type(data).__name__}")
    if isinstance(data, list):
        print(f"  Number of records: {len(data)}")
        if data:
            print(f"  Sample record keys: {list(data[0].keys())}")
    elif isinstance(data, dict):
        print(f"  Top-level keys: {list(data.keys())}")

import pandas as pd

def inspect_xlsx(path):
    xls = pd.ExcelFile(path)
    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet_name)
        print(f"  Sheet '{sheet_name}': {len(df)} data rows")
        print(f"    Columns: {list(df.columns)}")

def inspect_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    print(f"  Top-level type: {type(data).__name__}")
    if isinstance(data, dict):
        print(f"  Top-level keys: {list(data.keys())}")
    elif isinstance(data, list):
        print(f"  Number of records: {len(data)}")
        if data:
            print(f"  Sample record keys: {list(data[0].keys())}")

def inspect_xml(path):
    tree = ET.parse(path)
    root = tree.getroot()
    print(f"  Root tag: {root.tag}")
    children = list(root)
    print(f"  Number of child elements: {len(children)}")
    if children:
        print(f"  First child tag: {children[0].tag}")
        print(f"  First child sub-tags: {[c.tag for c in children[0]]}")


print("=" * 60)
print("MAP LPP PROJECT - SOURCE DATA STRUCTURE INSPECTION")
print("=" * 60)

for file in sorted(RAW_DATA_DIR.rglob("*")):
    if not file.is_file():
        continue
    print(f"\n{file.name}")
    print("-" * 60)
    try:
        ext = file.suffix.lower()
        if ext == ".json":
            inspect_json(file)
        elif ext == ".yaml" or ext == ".yml":
            inspect_yaml(file)
        elif ext == ".xml":
            inspect_xml(file)
        elif ext == ".xlsx":
            inspect_xlsx(file)
        else:
            print("  (no inspector for this format)")
    except Exception as e:
        print(f"  ERROR reading file: {e}")

print("\nStructure inspection completed.")