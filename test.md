# Acceptance Test Suite (test.md)

Each test verifies one Acceptance Criterion from `spec.md` against the live Google Sheet via the Test Bridge.

---

### Test T1: Version Reporting (AC 1)
- **Action**: `run { fn: "appVersion", args: [] }`
- **Expected Outcome**: `{ ok: true, result: "s5-v1" }` (or matching attempt version tag).

### Test T2: Sheet Setup & Tabs Creation (AC 2)
- **Precondition**: `run { fn: "resetApp", args: [] }` then `run { fn: "setupSheet", args: [] }`
- **Action**: `listTabs`
- **Expected Outcome**: `{ ok: true, tabs: [...] }` containing `"Sheet1"`, `"survey"`, `"mailing_list"`, and `"responses"`.

### Test T3: Tab Schema & Sample Data (AC 2)
- **Action 1**: `readTab { tab: "survey" }`
  - **Expected Outcome**: Header row `["Title", "Type", "Required", "Options"]` followed by 3 question rows including Scale `"1-5"`.
- **Action 2**: `readTab { tab: "mailing_list" }`
  - **Expected Outcome**: Header row `["Name", "Email", "Status"]` followed by at least one recipient matching authorized test emails.
- **Action 3**: `readTab { tab: "responses" }`
  - **Expected Outcome**: Header row `["Timestamp", "Your Name", "Community Role", "Overall Satisfaction"]`.

### Test T4: Form Generation (AC 3)
- **Action**: `run { fn: "generateForm", args: [] }`
- **Expected Outcome**: `{ ok: true, formUrl: "<url>" }`
- **Verification**: `formInfo { formUrl: "<url>" }`
  - **Expected Outcome**: Title `"Community Survey"`, 3 items with types `["TEXT", "MULTIPLE_CHOICE", "SCALE"]`.

### Test T5: Survey Email Distribution (AC 4)
- **Action**: `run { fn: "sendSurveys", args: [] }`
- **Expected Outcome**: `{ ok: true, sentCount: N }` where $N \ge 1$.
- **Verification 1**: `readTab { tab: "mailing_list" }` -> Status column contains `"Sent"`.
- **Verification 2**: `gmailSearch { query: "Community Survey" }` -> returns at least 1 email thread with subject containing `"Community Survey"`.

### Test T6: Form Response Submission & Sync (AC 5)
- **Action 1**: `submitResponse { formUrl: "<url>", answers: { "Your Name": "Alex Tester", "Community Role": "Professional", "Overall Satisfaction": 5 } }`
  - **Expected Outcome**: `{ ok: true }`
- **Action 2**: `run { fn: "syncResponses", args: [] }`
  - **Expected Outcome**: `{ ok: true, responseCount: N }` where $N \ge 1$.
- **Verification**: `readTab { tab: "responses" }`
  - **Expected Outcome**: Contains row with `"Alex Tester"`, `"Professional"`, and `"5"`.

### Test T7: Clean State Reset (AC 6)
- **Action**: `run { fn: "resetApp", args: [] }`
- **Expected Outcome**: `{ ok: true }`
- **Verification**: `listTabs` confirms `"Sheet1"` is present and was never deleted.

### Test T8: Custom Menu Appearance (AC 7) `[HUMAN]`
- **Action**: Human visual confirmation on the spreadsheet UI.
- **Expected Outcome**: Reload the Google Sheet and verify that a custom menu named `"Survey App"` appears in the top menu bar with menu items matching the spec.
