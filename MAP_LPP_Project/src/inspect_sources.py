
from pathlib import Path

# 1. Identify the project folder
PROJECT_DIR = Path(__file__).resolve().parent.parent

# 2. Identify the raw data folder
RAW_DATA_DIR = PROJECT_DIR / "data" / "raw"

# 3. Check whether the folder exists
if not RAW_DATA_DIR.exists():
    print("ERROR: The data/raw folder does not exist.")
    print(f"Expected location: {RAW_DATA_DIR}")
    raise SystemExit(1)

# 4. Get all files inside the raw data folder
files = [
    file for file in RAW_DATA_DIR.rglob("*")
    if file.is_file()
]

# 5. Display the folder location
print("=" * 60)
print("MAP LPP PROJECT - SOURCE FILE INSPECTION")
print("=" * 60)

print(f"Raw data folder: {RAW_DATA_DIR}")
print(f"Total files found: {len(files)}")

# 6. Display each file's details
print("\nSOURCE FILES")
print("-" * 60)

for file in sorted(files):
    extension = file.suffix.lower() or "[no extension]"
    size_kb = file.stat().st_size / 1024

    print(f"File name : {file.name}")
    print(f"Format    : {extension}")
    print(f"Size      : {size_kb:.2f} KB")
    print(f"Location  : {file.relative_to(PROJECT_DIR)}")
    print("-" * 60)

# 7. Count files by format
format_counts = {}

for file in files:
    extension = file.suffix.lower() or "[no extension]"
    format_counts[extension] = format_counts.get(extension, 0) + 1

print("\nFILE FORMAT SUMMARY")
print("-" * 60)

for extension, count in sorted(format_counts.items()):
    print(f"{extension}: {count} file(s)")

print("\nInspection completed successfully!")