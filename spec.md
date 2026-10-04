# Survey Application Specification (spec.md)

## 1. Overview
A lightweight community survey system built on Google Sheets, Google Forms, and Google Apps Script that generates a customized Google Form from sheet configuration, distributes it to a mailing list, and synchronizes submissions into a structured response sheet.

---

## 2. Acceptance Criteria (AC)

### AC 1: Version Reporting
- The function `appVersion()` must return the current version string (e.g. `"s5-v1"`).

### AC 2: Deterministic Sheet Setup
- The function `setupSheet()` must configure the active spreadsheet:
  - Preserves default tab `Sheet1`.
  - Creates tab `survey` with headers `["Title", "Type", "Required", "Options"]` formatted as plain text, populated with 3 sample questions:
    1. `"Your Name"` | `"Text"` | `"TRUE"` | `""`
    2. `"Community Role"` | `"Multiple Choice"` | `"TRUE"` | `"Student, Educator, Professional, Enthusiast"`
    3. `"Overall Satisfaction"` | `"Scale"` | `"TRUE"` | `"1-5"` (plain text format)
  - Creates tab `mailing_list` with headers `["Name", "Email", "Status"]`, populated with recipient rows using `TEST_EMAILS`.
  - Creates tab `responses` with headers `["Timestamp", "Your Name", "Community Role", "Overall Satisfaction"]`.
  - Calls `SpreadsheetApp.flush()`.
  - Returns `{ ok: true }`.

### AC 3: Form Generation
- The function `generateForm()` must:
  - Read questions from `survey` tab.
  - Create a new Google Form titled `"Community Survey"`.
  - Add items corresponding to each row:
    - `"Text"` -> `asTextItem()`
    - `"Multiple Choice"` -> `asMultipleChoiceItem()` with parsed comma-separated choices
    - `"Scale"` -> `asScaleItem()` with lower bound 1 and upper bound 5
  - Set `isRequired(true)` if Required column is `"TRUE"`.
  - Save the form URL and ID in Script Properties (`SURVEY_FORM_URL`, `SURVEY_FORM_ID`).
  - Return `{ ok: true, formUrl: form.getPublishedUrl(), formId: form.getId() }`.

### AC 4: Survey Distribution
- The function `sendSurveys()` must:
  - Retrieve the form published URL from Script Properties.
  - Read `mailing_list` rows.
  - Verify every recipient email against the authorized `TEST_EMAILS` safety filter.
  - Dispatch survey invitation emails via `MailApp.sendEmail` with subject `"Community Survey"` and body containing the published URL.
  - Mark `Status` column in `mailing_list` as `"Sent"`.
  - Call `SpreadsheetApp.flush()`.
  - Return `{ ok: true, sentCount: N }`.

### AC 5: Response Synchronization
- The function `syncResponses()` must:
  - Retrieve the active form from Script Properties.
  - Read all submitted responses from the Form.
  - Append new response rows into the `responses` tab matching the header schema.
  - Call `SpreadsheetApp.flush()`.
  - Return `{ ok: true, responseCount: N }`.

### AC 6: Clean State Reset
- The function `resetApp()` must:
  - Clear or delete tabs `survey`, `mailing_list`, and `responses`, never deleting `Sheet1`.
  - Remove stored form references from Script Properties.
  - Call `SpreadsheetApp.flush()`.
  - Return `{ ok: true }`.

### AC 7: User Interface Menu `[HUMAN]`
- An `onOpen()` trigger must register a top-level menu named `"Survey App"` with menu items:
  - `"Setup Sheet"` -> `setupSheet`
  - `"Generate Form"` -> `generateForm`
  - `"Send Surveys"` -> `sendSurveys`
  - `"Sync Responses"` -> `syncResponses`
  - `"Reset App"` -> `resetApp`

---

## 3. Appendix: How We Got Here
Every product decision recorded during the 3-round PM interview:

| Round | Question | Options Presented | Selected Answer | Rationale |
|---|---|---|---|---|
| **1.1** | Question types for `survey` tab | 1. Text, Multiple Choice, Scale (1-5) (Rec)<br>2. Text & MC only<br>3. Text only | **Text, Multiple Choice, Scale (1-5)** | Captures quantitative metrics and qualitative feedback in v0. |
| **1.2** | Email distribution trigger | 1. Manual function & menu item (Rec)<br>2. Combined with form generation<br>3. Row edit trigger | **Manual function & menu item** | Gives user explicit control before emails are dispatched. |
| **2.1** | Response collection method | 1. syncResponses() on-demand (Rec)<br>2. Link form directly<br>3. Time-driven poll | **syncResponses() on-demand** | Ensures responses populate into the exact `responses` tab specified in brief. |
| **2.2** | Sample data initialized | 1. 3 sample questions + TEST_EMAILS (Rec)<br>2. 2 questions + 1 recipient<br>3. Empty headers only | **3 sample questions + TEST_EMAILS** | Provides instant testability across all 3 question types while maintaining email safety. |
