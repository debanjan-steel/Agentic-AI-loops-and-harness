# Model Training Loop Specification

## 1. Objective & Success Metric
- **Goal**: Train a regression model predicting `MedHouseVal` from census features with **MAPE < 5.0%** on the validation set.
- **Metric**: Mean Absolute Percentage Error: $\text{MAPE} = \frac{100\%}{n} \sum \left|\frac{y - \hat{y}}{y}\right|$
- **Target Safety Check**: Target range is $[0.14999, 5.00001]$ (in \$100k). No zero or near-zero targets; MAPE will not divide by zero.

---

## 2. One-Time Data Preparation
1. **Dataset**: 20,640 rows, 8 features (`MedInc`, `HouseAge`, `AveRooms`, `AveBedrms`, `Population`, `AveOccup`, `Latitude`, `Longitude`), target `MedHouseVal`. No missing values.
2. **Data Split**: Fixed seed `random_state=42`.
   - **Train**: 70% (14,448 rows)
   - **Validation**: 15% (3,096 rows)
   - **Test**: 15% (3,096 rows) — **LOCKED** until after final attempt.
3. Split is saved once so every attempt and script uses the exact same partitions.

---

## 3. Harness & System Architecture
The loop operates strictly through three scripts and two log/artifact files:

- **`train.py`**:
  - Single parameterized training script.
  - Arguments: `--algorithm`, `--params`, `--attempt`, `--hypothesis`.
  - Fits on train set only, evaluates train MAPE & validation MAPE.
  - Logs one row to `experiments.csv`.
  - Saves `best_model.pkl` if validation MAPE is the lowest so far.
- **`analyze.py`**:
  - Reads validation predictions from the latest attempt.
  - Evaluates:
    1. Error distribution across price quartiles / extremes.
    2. Over- vs under-prediction tendencies.
    3. Geographic error clustering (correlations with Lat/Long).
  - Outputs empirical findings to inform the next written hypothesis.
- **`check_stop.py`**:
  - Independent stop criteria checker.
  - Reads `experiments.csv`.
  - Prints:
    - `SUCCESS`: if validation MAPE < 5.0%.
    - `STOP`: if attempts reach 5.
    - `CONTINUE`: otherwise.
- **`experiments.csv`**:
  - Columns: `attempt,algorithm,hyperparameters,hypothesis,train_mape,val_mape,overfit_gap,run_time_sec,supported,next_step`
- **`results.md`**:
  - Generated at completion. Contains summary table of all attempts, the winning model, test MAPE, and 3 key learnings.

---

## 4. Iteration Plan (Up to 5 Attempts)

| Attempt | Planned Model | Initial Rationale |
|---|---|---|
| **1** | Linear Regression | Establish a fast, interpretable linear baseline. |
| **2** | Random Forest Regressor | Capture non-linear feature interactions and non-parametric boundaries. |
| **3** | Gradient Boosted Decision Trees (GBDT) | Apply shrinkage and sequential boosting; regularize if Attempt 2 overfits. |
| **4** | Hypothesis-led adjustment | Driven by `analyze.py` findings (e.g. loss reweighting, log-target transform, or spatial features). |
| **5** | Hypothesis-led adjustment | Final refinement / hyperparameter regularisation guided by evidence. |

---

## 5. Loop Rules & Constraints
1. **Test Set Lock**: The test set is strictly evaluated once at the very end on `best_model.pkl`. `analyze.py` and `train.py` never access test data during training.
2. **Overfit Guardrail**: If `overfit_gap` ($\text{val\_mape} - \text{train\_mape}$) $> 5.0\%$, the subsequent attempt is required to introduce regularization (e.g. max_depth constraints, shrinkage, l2 penalty).
3. **Hypothesis-First Rule**: No attempt runs without an explicit hypothesis grounded in numbers from `analyze.py` or prior experiment rows.
4. **Honest Stop Authority**: The loop terminates only when `check_stop.py` returns `SUCCESS` or `STOP`. The agent cannot declare early finish.
5. **Reporting Protocol**: After each attempt, report exactly one line:
   `Attempt N | Change: <change> | Val MAPE: <X.X%> | Overfit Gap: <Y.Y>`
