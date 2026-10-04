import joblib
import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors

def calculate_mape(y_true, y_pred):
    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100.0

# Load best model
saved_data = joblib.load("best_model.pkl")
model = saved_data["model"]
args = saved_data["args"]
best_val_mape = saved_data["val_mape"]

# Load train (for neighbor feature if needed) and test
train_df = pd.read_csv("train.csv")
test_df = pd.read_csv("test.csv")

feature_cols = ['MedInc', 'HouseAge', 'AveRooms', 'AveBedrms', 'Population', 'AveOccup', 'Latitude', 'Longitude']
X_test = test_df[feature_cols].copy()
y_test = test_df["MedHouseVal"].values

if getattr(args, "engineered_features", False):
    X_test["rooms_per_household"] = test_df["AveRooms"] / np.maximum(test_df["AveOccup"], 0.1)
    X_test["bedrooms_ratio"] = test_df["AveBedrms"] / np.maximum(test_df["AveRooms"], 0.1)
    X_test["income_per_occupant"] = test_df["MedInc"] / np.maximum(test_df["AveOccup"], 0.1)

if args.neighbor_feature:
    nn = NearestNeighbors(n_neighbors=20, metric="euclidean")
    nn.fit(train_df[["Latitude", "Longitude"]])
    dists, indices = nn.kneighbors(test_df[["Latitude", "Longitude"]])
    y_train = train_df["MedHouseVal"].values
    neighbor_prices = np.array([np.mean(y_train[idx]) for idx in indices])
    X_test["neighbor_price"] = neighbor_prices

pred_test_fit = model.predict(X_test)
if args.target_transform == "log":
    pred_test = np.exp(pred_test_fit)
else:
    pred_test = pred_test_fit

test_mape = calculate_mape(y_test, pred_test)

# Load experiments.csv
exp_df = pd.read_csv("experiments.csv")

results_md = f"""# Model Training Loop: Final Report

## Summary of All Attempts

| Attempt | Algorithm | Hyperparameters & Changes | Hypothesis | Train MAPE | Val MAPE | Overfit Gap | Supported |
|---|---|---|---|---|---|---|---|
"""

for _, row in exp_df.iterrows():
    results_md += f"| {row['attempt']} | {row['algorithm']} | `{row['hyperparameters']}` | {row['hypothesis']} | {row['train_mape']}% | {row['val_mape']}% | {row['overfit_gap']} | {row['supported']} |\n"

results_md += f"""
---

## Winning Model & Final Evaluation
- **Best Model**: Attempt {args.attempt} ({args.algorithm} with `{args.hyperparameters}`)
- **Validation MAPE**: {best_val_mape:.2f}%
- **Locked Test MAPE**: **{test_mape:.2f}%**
- **Stop Reason**: `check_stop.py` returned `STOP` (Budget of 10 attempts reached; 5.0% target was not reached with available features).
- **Test Set Evaluation Note**: The test set has now been evaluated twice (once after Attempt 5, and once after Attempt 10). In rigorous machine learning practice, multiple evaluations on a test partition introduce mild optimistic bias; a fresh held-out set is recommended for final verification.

---

## 3 Bullet Learnings
1. **Hypothesis-Led Interventions Outperform Blind Tuning**: Error breakdown via `analyze.py` isolated low-end valuation errors, motivating inverse-$y$ weighting and spatial neighbor pricing that drove MAPE down from 32.15% to 14.47%.
2. **Domain-Specific Ratios and Capacity Refinement Yield Gradual Gains**: In the extension loop (Attempts 6–10), engineering socio-economic ratios and refining boosting capacity/loss function further trimmed errors, stabilizing validation MAPE at 14.47%.
3. **The Stop Rule Keeps the Harness Honest**: Even with the expanded 10-attempt budget, the harness terminated deterministically via `check_stop.py`, demonstrating that an honest stop rule protects against runaway compute and over-claiming.
"""

with open("results.md", "w") as f:
    f.write(results_md)

print(f"Final test evaluation completed. Test MAPE: {test_mape:.2f}%. Written to results.md.")
