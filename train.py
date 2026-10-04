import argparse
import time
import os
import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor
from sklearn.neighbors import NearestNeighbors

def calculate_mape(y_true, y_pred):
    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100.0

def main():
    parser = argparse.ArgumentParser(description="Unified model training script")
    parser.add_argument("--attempt", type=int, required=True)
    parser.add_argument("--algorithm", type=str, required=True, 
                        choices=["linear_regression", "random_forest", "gbdt"])
    parser.add_argument("--hyperparameters", type=str, default="")
    parser.add_argument("--hypothesis", type=str, required=True)
    parser.add_argument("--supported", type=str, default="yes")
    parser.add_argument("--next_step", type=str, default="")
    
    # Feature / Target engineering options
    parser.add_argument("--target_transform", type=str, default="none", choices=["none", "log"])
    parser.add_argument("--weighting", type=str, default="none", choices=["none", "inverse_y"])
    parser.add_argument("--neighbor_feature", action="store_true", default=False)
    parser.add_argument("--engineered_features", action="store_true", default=False)
    
    # Model hyperparameters
    parser.add_argument("--n_estimators", type=int, default=100)
    parser.add_argument("--max_depth", type=int, default=None)
    parser.add_argument("--learning_rate", type=float, default=0.1)
    parser.add_argument("--min_samples_leaf", type=int, default=20)
    parser.add_argument("--loss", type=str, default="squared_error")

    args = parser.parse_args()
    start_time = time.time()

    # Load data
    train_df = pd.read_csv("train.csv")
    val_df = pd.read_csv("val.csv")

    feature_cols = ['MedInc', 'HouseAge', 'AveRooms', 'AveBedrms', 'Population', 'AveOccup', 'Latitude', 'Longitude']
    X_train = train_df[feature_cols].copy()
    y_train = train_df["MedHouseVal"].values.copy()
    X_val = val_df[feature_cols].copy()
    y_val = val_df["MedHouseVal"].values.copy()

    # Optional: engineered ratio features
    if args.engineered_features:
        for df_curr, X_curr in [(train_df, X_train), (val_df, X_val)]:
            X_curr["rooms_per_household"] = df_curr["AveRooms"] / np.maximum(df_curr["AveOccup"], 0.1)
            X_curr["bedrooms_ratio"] = df_curr["AveBedrms"] / np.maximum(df_curr["AveRooms"], 0.1)
            X_curr["income_per_occupant"] = df_curr["MedInc"] / np.maximum(df_curr["AveOccup"], 0.1)

    # Optional: neighbor price feature (built from train rows only without leakage)
    if args.neighbor_feature:
        # Fit on train lat/long
        nn = NearestNeighbors(n_neighbors=21, metric="euclidean")
        nn.fit(train_df[["Latitude", "Longitude"]])
        
        # For train: exclude self (neighbor 1..20)
        train_dists, train_indices = nn.kneighbors(train_df[["Latitude", "Longitude"]])
        train_neighbor_prices = np.array([np.mean(y_train[idx[1:]]) for idx in train_indices])
        X_train["neighbor_price"] = train_neighbor_prices
        
        # For val: use 20 nearest train blocks
        val_dists, val_indices = nn.kneighbors(val_df[["Latitude", "Longitude"]], n_neighbors=20)
        val_neighbor_prices = np.array([np.mean(y_train[idx]) for idx in val_indices])
        X_val["neighbor_price"] = val_neighbor_prices

    # Target transform
    if args.target_transform == "log":
        y_train_fit = np.log(y_train)
    else:
        y_train_fit = y_train

    # Sample weighting
    sample_weight = None
    if args.weighting == "inverse_y":
        sample_weight = 1.0 / y_train

    # Algorithm selection
    if args.algorithm == "linear_regression":
        model = LinearRegression()
        model.fit(X_train, y_train_fit, sample_weight=sample_weight)
    elif args.algorithm == "random_forest":
        model = RandomForestRegressor(
            n_estimators=args.n_estimators,
            max_depth=args.max_depth,
            min_samples_leaf=args.min_samples_leaf,
            random_state=42,
            n_jobs=-1
        )
        model.fit(X_train, y_train_fit, sample_weight=sample_weight)
    elif args.algorithm == "gbdt":
        model = HistGradientBoostingRegressor(
            max_iter=args.n_estimators,
            max_depth=args.max_depth,
            learning_rate=args.learning_rate,
            min_samples_leaf=args.min_samples_leaf,
            loss=args.loss,
            random_state=42
        )
        model.fit(X_train, y_train_fit, sample_weight=sample_weight)

    # Predict
    pred_train_fit = model.predict(X_train)
    pred_val_fit = model.predict(X_val)

    if args.target_transform == "log":
        pred_train = np.exp(pred_train_fit)
        pred_val = np.exp(pred_val_fit)
    else:
        pred_train = pred_train_fit
        pred_val = pred_val_fit

    train_mape = calculate_mape(y_train, pred_train)
    val_mape = calculate_mape(y_val, pred_val)
    overfit_gap = val_mape - train_mape
    run_time = round(time.time() - start_time, 2)

    # Save validation predictions for analyze.py
    pd.DataFrame({"prediction": pred_val}).to_csv("val_preds.csv", index=False)

    # Check if best model so far
    is_best = True
    experiments_file = "experiments.csv"
    if os.path.exists(experiments_file):
        exp_df = pd.read_csv(experiments_file)
        if len(exp_df) > 0 and exp_df["val_mape"].min() <= val_mape:
            is_best = False

    if is_best:
        joblib.dump({"model": model, "args": args, "val_mape": val_mape}, "best_model.pkl")

    # Log to experiments.csv
    log_entry = {
        "attempt": args.attempt,
        "algorithm": args.algorithm,
        "hyperparameters": args.hyperparameters,
        "hypothesis": args.hypothesis,
        "train_mape": round(train_mape, 2),
        "val_mape": round(val_mape, 2),
        "overfit_gap": round(overfit_gap, 2),
        "run_time_sec": run_time,
        "supported": args.supported,
        "next_step": args.next_step
    }

    if not os.path.exists(experiments_file):
        pd.DataFrame([log_entry]).to_csv(experiments_file, index=False)
    else:
        exp_df = pd.read_csv(experiments_file)
        exp_df = pd.concat([exp_df, pd.DataFrame([log_entry])], ignore_index=True)
        exp_df.to_csv(experiments_file, index=False)

    print(f"SUCCESS_RUN attempt={args.attempt} val_mape={val_mape:.2f}% train_mape={train_mape:.2f}% gap={overfit_gap:.2f}")

if __name__ == "__main__":
    main()
