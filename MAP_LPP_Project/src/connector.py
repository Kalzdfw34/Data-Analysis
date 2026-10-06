import pandas as pd

file_path = r"D:\Pro IT Bridge\MAP_LPP_Project\data\processed\PROMOTION_TABLE.csv"

df = pd.read_csv(file_path)

duplicates = df[df.duplicated(subset=["SKU"], keep=False)]

print("Total rows:", len(df))
print("Unique SKUs:", df["SKU"].nunique())
print("Duplicate SKU rows:", len(duplicates))

print("\nDuplicate SKUs:")
print(duplicates.sort_values("SKU"))