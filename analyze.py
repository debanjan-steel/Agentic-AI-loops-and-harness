import pandas as pd
import numpy as np

val_df = pd.read_csv("val.csv")
preds_df = pd.read_csv("val_preds.csv")

y_true = val_df["MedHouseVal"].values
y_pred = preds_df["prediction"].values
abs_pct_err = np.abs((y_true - y_pred) / y_true) * 100

val_df["error"] = y_pred - y_true
val_df["abs_pct_error"] = abs_pct_err

print("=== VALIDATION ERROR ANALYSIS ===")
# 1. Price range breakdown (quartiles)
val_df["price_bin"] = pd.qcut(val_df["MedHouseVal"], q=4, labels=["Q1 (lowest)", "Q2", "Q3", "Q4 (highest)"])
price_analysis = val_df.groupby("price_bin", observed=False)["abs_pct_error"].mean()
print("\nMean MAPE by Price Quartile:")
for bin_name, mape in price_analysis.items():
    print(f"  {bin_name}: {mape:.2f}%")

# 2. Over vs Under prediction
over_pred = np.mean(y_pred > y_true) * 100
under_pred = np.mean(y_pred < y_true) * 100
print(f"\nOver-prediction: {over_pred:.1f}% | Under-prediction: {under_pred:.1f}%")

# Cheap homes specifically (y < 1.0)
cheap_mask = y_true < 1.0
if np.sum(cheap_mask) > 0:
    cheap_mape = np.mean(abs_pct_err[cheap_mask])
    cheap_bias = np.mean(y_pred[cheap_mask] - y_true[cheap_mask])
    print(f"Homes < $100k (count={np.sum(cheap_mask)}): MAPE={cheap_mape:.2f}%, Mean bias={cheap_bias:+.3f}")

# 3. Spatial error correlation
corr_lat = np.corrcoef(val_df["Latitude"], abs_pct_err)[0, 1]
corr_lon = np.corrcoef(val_df["Longitude"], abs_pct_err)[0, 1]
print(f"\nError correlation with Latitude: {corr_lat:.3f} | Longitude: {corr_lon:.3f}")
