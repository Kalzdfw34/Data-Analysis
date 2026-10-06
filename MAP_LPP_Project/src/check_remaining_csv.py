import pandas as pd

file_path = r"D:\Pro IT Bridge\MAP_LPP_Project\data\processed\PROMOTION_TABLE.csv"

df = pd.read_csv(file_path)

# Find duplicate combinations
duplicates = df[df.duplicated(
    subset=["PL", "SKU", "Season"],
    keep=False
)]

print("Number of duplicate rows:", len(duplicates))

print(duplicates.sort_values(
    by=["PL", "SKU", "Season"]
).to_string(index=False))