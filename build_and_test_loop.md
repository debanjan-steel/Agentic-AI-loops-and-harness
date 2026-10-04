# Build and Test Loop: Survey Application

## 1. Overview & Brief
**Goal**: Build a survey workflow application in Google Sheets + Google Forms + Google Apps Script that:
1. Generates a Google Form based on questions defined in the `survey` tab.
2. Distributes the published form via email to members listed in the `mailing_list` tab.
3. Automatically collects and stores submitted form responses in the `responses` tab.

---

## 2. Four Agent Roles & Responsibilities

| Role | File Owned | Responsibilities |
|---|---|---|
| **Product Manager (PM)** | `spec.md`, `test.md` | Conducts a focused 3-round interview (2–3 questions per round with recommendations) to define user requirements. Writes `spec.md` (with an appendix documenting all Q&A decisions) and `test.md` (one bridge-verifiable test per acceptance criterion). |
| **Software Engineer (SE)** | `code.gs` | Implements the Apps Script solution based strictly on `spec.md`. Includes `setupSheet()` (creates standard tabs/headers/sample rows), `resetApp()` (cleans tabs and unlinks old form), and `appVersion()` (returns version label `s5-vN`). All public functions return small JSON objects. On retries, reads `feedback.md` and modifies only what failed. |
| **Tester** | `feedback.md` | Executes every test in `test.md` against the live Google Sheet and Form exclusively via HTTPS calls to the Test Bridge. Never inspects code. Writes `feedback.md` detailing failed tests and expected vs. actual outcomes. |
| **Loop Engineer** | `loop_log.md`, `bridge.py` | Initiates after human approval of `spec.md`. Orchestrates preflight checks, pushes atomic code releases via the Deploy Bridge, verifies version propagation, triggers the Tester, and coordinates the iteration cycle up to 5 attempts. |

---

## 3. Google Workspace Connection Architecture
- **Environment Wrapper (`bridge.py`)**: Reads `TEST_BRIDGE_URL`, `TEST_BRIDGE_SECRET`, `DEPLOY_BRIDGE_URL`, `DEPLOY_BRIDGE_SECRET`, `SCRIPT_ID`, and `TEST_EMAILS` from `.env`. Never hardcodes or logs secrets.
- **Preflight Verification**: Executes `{"action": "check"}` on both bridges and `{"action": "getContent", "scriptId": SCRIPT_ID}` on the Deploy Bridge prior to Attempt 1.
- **Atomic Deployment**: Releases code using `{"action": "release", "scriptId": ..., "deploymentId": ..., "files": [...]}`. Every release delivers all three required project files: `appsscript`, `test_bridge`, and `Code`.
- **Release Verification**: Polls `run appVersion` until the new version identifier is returned consistently 3 times consecutively before starting tests (accounting for up to 90s propagation lag).

---

## 4. Harness Rules
1. **Email Safety Boundary**: Emails are strictly sent to addresses in `TEST_EMAILS`. No external or live community recipients.
2. **Deterministic State Reset**: Every attempt starts by executing `resetApp()` followed by `setupSheet()`. The default tab `Sheet1` is permanently preserved and never deleted.
3. **Strict File Ownership**: Each agent may only modify the file(s) it owns. Cross-agent communication happens via file artifacts.
4. **Secret Preservation**: Neither `setupTestBridge` nor `setupBridge` may ever be executed, preventing secret regeneration and connection drop.
5. **Human Inspection Boundary**: Any criteria that cannot be verified programmatically over HTTP (e.g., custom UI menu appearance) is flagged as `[HUMAN]` and deferred to a single manual check at the conclusion.
6. **Explicit Permissions**: If an Apps Script permission dialog is triggered, stop and prompt the user to authorize manually via the Apps Script IDE.

---

## 5. Known Pitfalls & Countermeasures
- **Spreadsheet Date Coercion**: Values like `"1-5"` can be auto-converted into dates by Sheets. Header and option columns are explicitly formatted as plain text (`@`) and parsed defensively.
- **Asynchronous Write Latency**: Values read immediately after execution may appear empty. All Apps Script data-writing functions must conclude with `SpreadsheetApp.flush()`.
- **Version Staling**: Cloud propagation delay may cause tests to hit previous script revisions. Version polling enforces triple confirmation of the new unique version tag (e.g. `s5-v1`, `s5-v2`).
- **Transient Network HTML Responses**: Apps Script endpoints occasionally return HTML error pages during peak load. `bridge.py` retries failed requests up to 3 times with exponential backoff before logging an error.
