from sklearn.datasets import fetch_california_housing
import pandas as pd

housing = fetch_california_housing(as_frame=True)
df = housing.frame
df.to_csv("data.csv", index=False)

print(f"Number of rows: {len(df)}")
print(f"Columns: {list(df.columns)}")
print(f"MedHouseVal min: {df['MedHouseVal'].min()}")
print(f"MedHouseVal max: {df['MedHouseVal'].max()}")
