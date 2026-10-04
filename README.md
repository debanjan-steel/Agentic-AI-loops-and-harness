# Agentic AI: Loops, Agents & Harnesses

This repository demonstrates autonomous AI workflows built around three core pillars of practical agentic systems:
1. **The Loop:** A goal, a scoreboard, and an un-overruleable stop rule.
2. **Multi-Agent Orchestration:** Strict separation of roles and coordination across specialized agents.
3. **The Harness:** Robust constraints, safety boundaries, and error recovery patterns that make agent execution reliable.

---

## Architecture & Systems

### 1. Autonomous Model Training Loop (`Part 1`)
- **Objective:** Predict `MedHouseVal` from the California Housing dataset with strict convergence criteria.
- **Stop Rule Authority:** Regulated by [`check_stop.py`](check_stop.py), preventing the agent from declaring premature success or spinning indefinitely.
- **Overfit Guardrail:** If overfit gap exceeds 5.0 points, the next iteration is required to regularize.
- **Empirical Evolution:** Guided by [`analyze.py`](analyze.py) error breakdown across price tiers and spatial coordinates, cutting validation MAPE from 32.15% to 14.47% (13.95% on locked test set).
- **Artifacts:** Full history documented in [`experiments.csv`](experiments.csv) and [`results.md`](results.md).

### 2. Google Workspace Bridge System (`Part 2`)
- **Test Bridge (`bridge_files/test_bridge.gs`):** Web app deployed to Google Apps Script providing HTTPS endpoints for agents to read/write sheet tabs, inspect Google Forms, submit responses, and search Gmail threads without human UI interaction.
- **Deploy Bridge (`bridge_files/deployer_bridge.gs`):** Standalone web app interfacing with Google Apps Script REST API to push atomic versioned code releases to live sheet projects.

### 3. Four-Agent App Building & Testing Loop (`Part 3`)
- **Product Manager (PM):** Conducted interactive requirements discovery, producing [`spec.md`](spec.md) and [`test.md`](test.md).
- **Software Engineer (SE):** Authored [`code.gs`](code.gs) implementing automated Google Form generation, email dispatch to mailing lists, and response synchronization.
- **Tester:** Executed acceptance tests exclusively through the HTTPS Test Bridge (never grading code directly), logging feedback to [`feedback.md`](feedback.md).
- **Loop Engineer:** Orchestrated atomic releases, polled version propagation via [`bridge.py`](bridge.py), and drove the build-test cycle to 100% test pass on Attempt 2 (logged in [`loop_log.md`](loop_log.md)).

---

## Project Structure

```
├── .env.example             # Template for Workspace bridge credentials
├── .gitignore               # Protects secrets (.env) and Python artifacts
├── README.md                # Project documentation
├── analyze.py               # Validation error analysis script
├── bridge.py                # Python wrapper for Workspace bridge calls
├── bridge_files/
│   ├── deployer_appsscript.json  # Deploy bridge manifest
│   ├── deployer_bridge.gs        # Deploy bridge implementation
│   ├── sheet_appsscript.json     # Test bridge manifest
│   └── test_bridge.gs            # Test bridge implementation
├── build_and_test_loop.md   # Multi-agent coordination specification
├── check_stop.py            # Objective termination rule script
├── code.gs                  # Production Google Apps Script application code
├── data.csv                 # California Housing dataset
├── download_data.py         # Initial data ingestion script
├── evaluate_test.py         # Locked test partition evaluator
├── experiments.csv          # Experiment tracking scoreboard
├── feedback.md              # Tester agent feedback log
├── loop_log.md              # Loop Engineer release and test log
├── prepare_data.py          # Fixed-seed data partitioning script
├── results.md               # Final model training synthesis report
├── run_tests.py             # Acceptance test runner
├── session_5.md             # Curriculum guide
├── spec.md                  # Approved application product specification
├── test.md                  # Acceptance test specifications
├── train.py                 # Parameterized regression training engine
└── training_loop.md         # Model training loop specification
```

---

## Setup & Running

### Requirements
- Python 3.10+
- `scikit-learn`, `pandas`, `numpy`, `joblib`

```bash
pip install scikit-learn pandas numpy joblib
```

### Running Model Loop
```bash
python train.py --attempt 1 --algorithm linear_regression --hypothesis "Baseline"
python analyze.py
python check_stop.py
```

### Running Workspace Loop
1. Copy `.env.example` to `.env` and configure your Google Apps Script Web App URLs and secrets.
2. Verify connectivity:
```bash
python bridge.py
```
3. Run the automated test suite:
```bash
python run_tests.py s5-v2
```
