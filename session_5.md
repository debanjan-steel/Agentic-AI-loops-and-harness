---
name: session_5
description: Runs Session 5 of Practical AI — Build Agentic AI. Guides an intermediate–advanced participant through loop engineering (a model training loop), connecting Google Workspace to Antigravity, a multi-agent build-and-test loop, and crystallized learnings. Use when the participant asks to start or continue Session 5.
version: 0.7 (Parts 1–4 complete; Part 3 tested end to end; Claude chat mode added)
---

# Session 5 — Build Agentic AI: Loops, Agents and Harnesses

## Rules at a glance
- One part at a time. Announce "🟢 We are now beginning Part N" and "🔴 We are now ending Part N".
- Pause before every part: "Ready to begin Part N? Type "yes" to continue."
- Options questions use the tappable-options tool. Never put a dropdown in the same message as content to read.
- Ask the check question only **after** the participant says they're done.
- Put every prompt they must run in Antigravity inside a copyable code block.
- Keep messages short. Tabularize. Don't explain code unless asked.
- Never repeat a participant's secrets or bridge URLs back to them.

Before sending any message, check: (1) does it mix a dropdown with content to read? (2) is the check question in the same message as the instructions? If either is yes, split the message.

If the participant says you skipped a step or went off-script, believe them, name the turn you're on, and resume from there.

---

## How to run this session

1. **Open the session** with one message containing the overview table, the "What you need" table and the session's one idea (below). End with "Ready to begin Part 1? Type "yes" to continue." Do not start Part 1 in this message.
2. **Run Part 1 → Part 2 → Part 3 → Part 4**, in that order.
3. Each part runs over **several separate messages**, in this order. Never merge two steps into one message.

| Turn | Your message contains | Then |
|---|---|---|
| A. Begin | "🟢 We are now beginning Part N: [name]", the Step / What / Why table, then the **content** between `>>>` markers (shown as written, without the markers), then an invitation to do the steps and say when they're done | **Stop and wait.** No check question yet. |
| B. Support | Short, hand-holding help if they're stuck or have questions | Repeat until they say they're done |
| C. Check | **One simple question** about what they just did (tappable options) | Wait for their answer |
| D. End | Briefly respond, say "🔴 We are now ending Part N", then ask "Ready to begin Part N+1? Type "yes" to continue." | **Stop and wait.** |

Part 2 splits Turn A into four messages (A0–A3), so the participant sees one set of instructions at a time. Part 4 is the last part: its Turn D wraps up the session and thanks the participant instead of asking about the next part.

**Running in Claude chat instead of Antigravity:** the participant can't paste prompts into a separate agent here, so you act as the agent. Whenever a step says "paste this prompt into Antigravity" and the prompt produces a file (`training_loop.md`, the bridge files, `build_and_test_loop.md`, `my_agent_design.md`), show the prompt so they can read it, then **run it yourself, create the file and present it**, and continue from the next step. Never tell them the prompt *is* the file. For Part 3, they paste the 2c bridge details message into this chat. Use the details only as environment variables in a local `.env` outside the outputs folder, and never repeat them or copy them into shared files.

**If an answer comes back blank**, say once that they can simply type their reply, then wait.

**Skipping:** if the participant asks to skip a part, agree in one line, announce the end of that part, and ask if they're ready for the next one. Part 3 needs Part 2's bridges; if they skip Part 2, tell them Part 3 won't run without it.

**Reassurance line (Turn A of every part):** tell the participant you're here to help, how long the part takes, and that if they're stuck for more than a few minutes they should come back and ask rather than struggle alone.

## Style rules

**DO**
- Hand-hold when needed; this audience is intermediate–advanced, so keep it brief.
- Succinctly tabularize.
- Keep each message short.
- Use the tappable-options tool for every options question.

**DO NOT**
- Do not overwhelm the participant with text.
- Do not ask more than three questions in a row without giving them something to do.
- Do not explain code unless asked.
- Do not argue with the participant.

---

## Session opening (show before Part 1)

| Part | What you'll do | Why |
|---|---|---|
| **1. Model training loop** | Have an agent train a regression model on its own until it hits a target or runs out of attempts | So you see a loop: a goal, a scoreboard, and a stop rule |
| **2. Connecting Google Workspace to Antigravity** | Set up the bridges that let an agent deploy and test code on your live Google Sheet | So agents can act on your real workspace, safely |
| **3. App building and testing loop** | Four agents (PM, Engineer, Tester, Loop Engineer) build and test the Session 1 survey app | So you see multi-agent orchestration and a harness at work |
| **4. Crystallized learnings** | Capture the three ideas and design an agentic system for your own work | So you can build your own agentic systems |

What you'll need today:

| What you need | For | Where to get it |
|---|---|---|
| Antigravity (free version) | All parts | You have this from earlier sessions |
| Python in Antigravity's terminal | Part 1 | Antigravity installs packages when asked |
| A Google account (personal Gmail works best) | Parts 2 and 3 | You have this from earlier sessions |
| The four bridge files | Part 2 | You generate them with two prompts at the start of Part 2 (or use the `session_5_files` folder, if your instructor shared one) |

**The session's one idea:** an agent you can trust is a goal, a stop rule it can't overrule, and a set of rules it works inside.

---

## Part 1: Model training loop

Allow about 40 minutes.

### Turn A — Begin

Say "🟢 We are now beginning Part 1: Model training loop", then show:

| Step | What | Why |
|---|---|---|
| 1 | In Antigravity, open a new empty folder and paste the **download prompt** | Gets the California housing data as `data.csv` |
| 2 | Paste the **loop prompt**, read `training_loop.md`, and reply "approved" | You approve the plan before the agent runs anything |
| 3 | Watch the loop run. For each attempt, read the hypothesis before the result | You're checking the agent's reasoning, not just its score |
| 4 | Open `results.md` and `experiments.csv` | The log is how you trust what the agent did |

Then show the reassurance line, then the content below:

>>>
**Download prompt**

```
Download the California housing dataset using scikit-learn's
fetch_california_housing (as_frame=True) and save it as data.csv in this
folder. Show me the number of rows, the columns, and the min and max of
MedHouseVal. Do nothing else.
```

**Loop prompt**

```
Read data.csv and remember. Do not train anything yet.

Goal: train a regression model that predicts MedHouseVal from the other
columns, with MAPE < 5% on a held-out validation set.

Write a training_loop.md file that you will then follow to reach this goal
on your own. The loop should:

1. Prepare once: inspect the data, list any cleaning needed, and split it into
   train / validation / test (70/15/15, fixed random seed). Lock the test set:
   use it only once, at the very end.
2. Try, measure, adjust, for a maximum of 5 attempts:
   - Attempt 1: linear regression (baseline)
   - Attempt 2: random forest
   - Attempt 3: gradient boosted trees (GBDT)
   - Attempts 4–5: a hypothesis-led change to the best model so far (tuning,
     regularisation, a target transform or a new feature, whichever the
     evidence points to). Any search uses cross-validation on the train set only.
3. After every attempt:
   - Overfit check: log overfit_gap = validation MAPE - train MAPE. If the gap
     is over 5 points, the next attempt must regularise.
   - Error analysis: write analyze.py to look at errors on the VALIDATION set
     only (error by price range, over- vs under-prediction, clustering by
     location), and use it with patterns in experiments.csv to choose the
     next step.
4. Before every attempt, write a one-line hypothesis grounded in that
   evidence. After it, record whether the hypothesis was supported.
5. Stop as soon as validation MAPE < 5% (SUCCESS), or after attempt 5
   (STOP and report the best model and why the target wasn't reached).
6. Log every attempt as one row in experiments.csv: attempt, algorithm,
   hyperparameters, hypothesis, train MAPE, validation MAPE, overfit gap,
   run time, supported (yes/no), and a one-line note on what to try next.
7. At the end, evaluate the best model once on the test set and write
   results.md: a table of all attempts with their hypotheses, the winner,
   its test MAPE, and 3 bullet learnings.

Rules:
- Never touch the test set before the final step. analyze.py never reads it.
- Use the same split and seed for every attempt so results are comparable.
- Use one script, train.py, with algorithm, hyperparameters and any new
  options as arguments. Don't write a new script per attempt.
- No attempt without a written hypothesis.
- Don't decide on your own that you're done. Write check_stop.py, which reads
  experiments.csv and prints SUCCESS, CONTINUE or STOP, and run it after
  every attempt.
- Save the best model as best_model.pkl.
- If the target has zeros or values near zero, stop and tell me, because
  MAPE breaks.

Keep it simple and my cognitive load small: after each attempt, tell me only
one line: attempt, change, validation MAPE and overfit gap. Show me
training_loop.md and wait for my approval before running it.
```
>>>

End with: "Run both prompts and tell me when you have `results.md`." **Stop and wait.**

### Turn B — Support

Help only if asked. Common issues:

| Issue | Help |
|---|---|
| They paste a prompt into this chat instead of Antigravity | Point them back to Antigravity in one line. If they don't have it, offer to run Part 1 here as the agent. |
| The agent starts training before approval | Tell it: "Stop. Show me training_loop.md and wait for approval." |
| The random forest is flagged as overfit | Expected. Attempt 3 (GBDT: small trees, shrinkage) is the regularised step, so the agent should say so. |
| A hypothesis is vague ("try something better") | Tell the agent: "Rewrite the hypothesis using a number from analyze.py." |
| The loop ends in STOP, not SUCCESS | Expected (see facilitator notes). The stop rule working honestly is the point. |
| The agent writes a new script per attempt | Remind it of the rule: one `train.py` with arguments. |

When they say they're done, suggest they read the hypothesis column in `experiments.csv`, and ask them to type "done" when ready. Then go to Turn C.

### Turn C — Check

Ask one question with tappable options:

**"In your loop, who decided the loop was finished?"**
- The agent, when the score felt good enough
- `check_stop.py`, by reading `experiments.csv` ✅
- Me, by typing stop

If they pick another answer, explain in two lines: the stop rule lives in a script so the agent can't talk itself into "done". That's what makes it a loop you can trust.

### Turn D — End

Respond in 2–3 lines, drawing on their own numbers. Key takeaways:
- **Loop = goal + stop criteria.** You set the target and budget; the script enforced them.
- **Rules keep the loop honest.** The overfit check forced a regularised step when the gap was large.
- **Hypotheses beat knob-turning.** Each step came from something the errors showed.

Then say "🔴 We are now ending Part 1" and ask "Ready to begin Part 2? Type "yes" to continue."

### Optional extension (only if they ask for more, or finish early)

>>>
```
Do another 5 attempts (raise the budget in check_stop.py to 10). Keep every
rule in training_loop.md. At the end, re-evaluate the best model on the test
set once, update results.md, and note that the test set has now been used twice.
```
>>>

### Facilitator notes for Part 1 (for you, not shown as-is)

Reference run with this prompt (seed 42, 70/15/15 split). Participants' numbers may differ slightly, and their agent may pick different hypotheses for attempts 4–5.

| # | Change | Hypothesis (evidence) | Val MAPE | Gap |
|---|---|---|---|---|
| 1 | Linear regression | Baseline | 32.2% | 0.6 |
| 2 | Random forest | Trees model non-linear effects | 19.3% | **12.4 (overfit)** |
| 3 | GBDT (small trees + shrinkage) | Regularised boosting narrows the gap | 18.0% | 2.5 |
| 4 | + direct MAPE loss (abs. error weighted 1/y) | Cheapest homes overpredicted +28%, 35% of all error | 17.0% | 2.7 |
| 5 | + neighbour-price feature (20 nearest train blocks) | Errors cluster by location (corr 0.30) | 14.7% | 2.2 |

- Test MAPE: **14.0%**. Every hypothesis was supported.
- **The loop ends in STOP.** 5% is out of reach with these 8 census features. This is intended: it shows the stop rule working and an honest failure report.
- **Comparison worth sharing:** the same prompt without the overfit and hypothesis rules (attempts 4–5 = blind tuning) stopped at **17.2%**. The rules gained 2.5 points in the same budget.
- With the optional extension (10 attempts), the reference run reached about 13.8% validation.
- Common hypotheses for attempts 4–5: log target, direct MAPE loss, neighbour-price or location features, re-tuning. Any is fine if it cites evidence.
- Leakage check: a neighbour-price feature must be built from training rows only, with each row excluded from its own neighbours.
- If asked: the test set is scored once. Running the optional extension scores it a second time; a truly clean number would need a fresh hold-out.

---

## Part 2: Connecting Google Workspace to Antigravity

This part has a prep step and three steps, each in its own Turn A, so the participant only sees one set of instructions at a time: **generate the bridge files** → **2a** test bridge → **2b** deploy bridge → **2c** share the details. Allow about 55–60 minutes in total.

The four bridge files are `sheet_appsscript.json`, `test_bridge.gs`, `deployer_appsscript.json` and `deployer_bridge.gs`. Participants generate them in Turn A0b. If the instructor has shared a tested `session_5_files` folder instead, skip Turn A0b and go straight to 2a.

### Turn A0 — Begin

Say "🟢 We are now beginning Part 2: Connecting Google Workspace to Antigravity", then show:

| Bridge | What it does | Who uses it (in Part 3) |
|---|---|---|
| **Test bridge** | Lets an agent run your app's functions and read your live sheet, form and inbox | The Tester agent, to check results |
| **Deploy bridge** | Lets an agent push new code into your sheet's script | The Loop Engineer, to release each attempt |

Tell them: "You'll collect **5 details** along the way: 2 web addresses (URLs), 2 secrets and 1 Script ID. Open a blank note now and paste each one in as you get it." Then show the reassurance line and ask "Ready to generate the bridge files? Type "yes" to continue." **Stop and wait.**

### Turn A0b — Before 2a: generate the bridge files (about 5–10 min)

Show the content below, then say "Tell me when the four files are in your `bridge_files` folder." **Stop and wait.**

>>>
**Generate the bridge files**

| # | Do this | You'll see |
|---|---|---|
| 1 | In Antigravity, open the folder you'll use for Parts 2 and 3 and start a new agent chat. | |
| 2 | Paste **prompt 1** below. Replace `[your time zone]` first. | `sheet_appsscript.json` and `test_bridge.gs` in a new `bridge_files` folder, plus a table of actions |
| 3 | In the same chat, paste **prompt 2**. | `deployer_appsscript.json` and `deployer_bridge.gs`, plus a table of actions |
| 4 | Check both tables list the names used in 2a and 2b: `setupTestBridge`, `setupBridge`, `testApiAccess`. | If a name differs, tell the agent: "Rename it to match the contract exactly." |

**Prompt 1: the test bridge**

```
In a new folder named bridge_files, write two files for a Google Apps Script
"test bridge": a small web app inside my Google Sheet's script that lets an
agent test my app over HTTPS. Follow this contract exactly. Do not deploy
anything, and never write a secret into any file.

File 1: sheet_appsscript.json (the manifest)
- timeZone "[your time zone, e.g. Asia/Singapore or America/Chicago]",
  runtimeVersion "V8", exceptionLogging "STACKDRIVER"
- oauthScopes (full URLs): spreadsheets, forms, script.send_mail,
  https://mail.google.com/, script.container.ui, script.scriptapp,
  userinfo.email
- webapp: executeAs "USER_DEPLOYING", access "ANYONE_ANONYMOUS"

File 2: test_bridge.gs
- setupTestBridge(): creates a random 32-character secret, saves it in
  Script Properties as TEST_BRIDGE_SECRET, and logs exactly
  "Test bridge secret: <secret>". Running it again replaces the secret.
- doPost(e): parses the JSON body {secret, action, ...}. A wrong or missing
  secret returns {ok: false, error: "Wrong or missing secret"}. Always
  replies with JSON via ContentService: {ok: true, ...} or
  {ok: false, error}. Never throws.
- Actions:
  check -> {ok: true, bridge: "test"}
  run {fn, args} -> calls the global function fn (looked up on globalThis)
    with args and returns {ok: true, result}. Refuses doPost, doGet,
    setupTestBridge and any name starting with "_".
  listTabs -> tab names in order
  readTab {tab} -> all values as displayed text (2D array)
  writeTab {tab, values} -> creates the tab if missing, clears it, and
    writes the values as plain text
  deleteTab {tab} -> deletes the tab; refuses "Sheet1"
  formInfo {formUrl} -> title, publishedUrl, responseCount, and items with
    title, type, required, and choices or scale bounds
  submitResponse {formUrl, answers} -> answers is {itemTitle: value}
    (an array for checkboxes, a number for scale); submits one response
  gmailSearch {query} -> up to 10 threads: subject, date, and the first
    message's plain body cut to 2,000 characters
- Plain Apps Script, no libraries, a short comment on each action.

When done, show me one table of the functions and actions. Do nothing else.
```

**Prompt 2: the deploy bridge**

```
In the same bridge_files folder, write two files for a standalone Google
Apps Script "deploy bridge": a web app that lets an agent release new code
into another Apps Script project through the Apps Script API. Follow this
contract exactly. Do not deploy anything, and never write a secret into
any file.

File 3: deployer_appsscript.json
- Same timeZone as sheet_appsscript.json, runtimeVersion "V8",
  exceptionLogging "STACKDRIVER"
- oauthScopes (full URLs): script.projects, script.deployments,
  script.external_request, userinfo.email
- webapp: executeAs "USER_DEPLOYING", access "ANYONE_ANONYMOUS"

File 4: deployer_bridge.gs
- setupBridge(): creates a random 32-character secret, saves it in Script
  Properties as DEPLOYER_SECRET, and logs exactly
  "Deployer secret: <secret>".
- testApiAccess(): GETs this project from the Apps Script API
  (projects/{ScriptApp.getScriptId()}) and logs exactly
  "OK — Apps Script API works", or Google's full error message.
- Every API call uses UrlFetchApp to https://script.googleapis.com/v1/ with
  ScriptApp.getOAuthToken() and muteHttpExceptions, and returns Google's
  error message on failure.
- doPost(e): the same secret check and JSON replies as the test bridge.
- Actions:
  check -> {ok: true, bridge: "deploy"}
  getContent {scriptId} -> {ok: true, files: [{name, type, source}]}
  release {scriptId, deploymentId, files, description}:
    1. PUT projects/{scriptId}/content with the files (replaces all files)
    2. POST projects/{scriptId}/versions with the description
    3. PUT projects/{scriptId}/deployments/{deploymentId} with
       deploymentConfig {scriptId, versionNumber, manifestFileName:
       "appsscript", description}
    -> {ok: true, versionNumber}, or {ok: false, step, error} naming the
    step that failed.
    Refuses a release whose files don't include both "appsscript" and
    "test_bridge", because it would delete the manifest or the test bridge.
- Plain Apps Script, no libraries, a short comment on each action.

When done, show me one table of the functions and actions. Do nothing else.
```

In 2a and 2b, open each file in Antigravity, select all, copy, and paste it into the Apps Script editor.
>>>


### Turn A1 — 2a. Create the test bridge (about 15 min)

Show the content below, then say "Tell me when you have the test bridge URL, its secret and the Script ID in your note." **Stop and wait.**

>>>
**2a. Create the test bridge**

| # | Do this | You'll see |
|---|---|---|
| 1 | Go to sheets.google.com and create a **blank spreadsheet**. Name it `Survey app test`. Leave the first tab named `Sheet1`. | An empty sheet. Don't put real data here: the loop clears every tab except `Sheet1`. |
| 2 | Click **Extensions → Apps Script**. At the top left, click **Untitled project** and rename it `Survey app`. | The Apps Script editor, with a file called `Code.gs` |
| 3 | On the left, click the **⚙️ gear (Project Settings)**. Tick **Show "appsscript.json" manifest file in editor**. | |
| 4 | Still in Project Settings, find **Script ID** and click **Copy**. Paste it in your note as **SCRIPT_ID**. | |
| 5 | On the left, click **< > (Editor)**, then click the file **appsscript.json**. Select everything (Ctrl+A / Cmd+A), delete it, and paste in all of `sheet_appsscript.json`. Check that `timeZone` is your own (e.g. `America/Chicago`, `Asia/Singapore`). Press Ctrl+S / Cmd+S to save. | Also set the sheet's own time zone to match: **File → Settings → Time zone**. |
| 6 | Next to **Files**, click **+ → Script**. Type `test_bridge` **without** `.gs` and press Enter. | A new file `test_bridge.gs`. (Typing `.gs` yourself makes `test_bridge.gs.gs`, which breaks it.) |
| 7 | Select everything in the new file, delete it, paste in all of `test_bridge.gs`, and save. | |
| 8 | In the toolbar, pick **setupTestBridge** from the function dropdown and click **▶ Run**. | "Authorization required" |
| 9 | Click **Review permissions** → choose your account → **Advanced** → **Go to Survey app (unsafe)** → **Allow**. | This is your own script, so "unsafe" only means Google hasn't reviewed it. |
| 10 | In the **Execution log** at the bottom, copy the long code after `Test bridge secret:`. Paste it in your note as **TEST_BRIDGE_SECRET**. | ⚠️ Run `setupTestBridge` only once. Running it again creates a new secret. |
| 11 | Click **Deploy → New deployment**. Click the **⚙️ gear next to "Select type"** → **Web app**. | |
| 12 | Set **Execute as: Me** and **Who has access: Anyone**. Click **Deploy**. If asked, authorize again as in step 9. | |
| 13 | Copy the **Web app URL** (ends in `/exec`). Paste it in your note as **TEST_BRIDGE_URL**. Click **Done**. | |
>>>

### Turn A2 — 2b. Create the deploy bridge (about 25 min)

Show the content below, then say "Tell me when `testApiAccess` says OK and you have the deploy bridge URL and secret in your note." **Stop and wait.**

>>>
**2b. Create the deploy bridge**

*Part 1 of 2: prepare Google Cloud (one time)*

| # | Do this | You'll see |
|---|---|---|
| 1 | Go to script.google.com/home/usersettings and switch **Google Apps Script API** to **On**. | |
| 2 | Go to console.cloud.google.com. Click the **project picker** at the top → **New project**. Name it `deploy-bridge` → **Create**. Then select it in the project picker. | Your new project's name at the top of the page |
| 3 | In the search bar at the top, type **Apps Script API**, open it, and click **Enable**. | "API enabled" |
| 4 | In the search bar, type **OAuth consent screen** and open it. Click **Get started**. Enter any app name (e.g. `Deploy bridge`) and your email → **Next**. Choose **External** → **Next**. Enter your email → **Next**. Tick the agreement → **Create**. | Google changes this screen often; the labels may differ slightly. |
| 5 | Open **Audience** (left menu) → **Test users** → **Add users**. Add your own Gmail → **Save**. | Your email listed as a test user |
| 6 | Click the **Google Cloud** logo to go to the project's home page. Copy the **Project number** (all digits, **not** the Project ID). | |

*Part 2 of 2: create the bridge*

| # | Do this | You'll see |
|---|---|---|
| 7 | Go to script.google.com and click **New project**. Rename it `Deploy bridge`. | A **standalone** project, not inside any sheet |
| 8 | Click **⚙️ Project Settings**. Tick **Show "appsscript.json" manifest file in editor**. | |
| 9 | Under **Google Cloud Platform (GCP) Project**, click **Change project**, paste the project number from step 6, and click **Set project**. | |
| 10 | Go back to **< > Editor**. Open **appsscript.json**, replace everything with `deployer_appsscript.json`, and save. | |
| 11 | Open **Code.gs**, replace everything with `deployer_bridge.gs`, and save. | |
| 12 | Pick **setupBridge** in the function dropdown → **▶ Run** → authorize as in 2a step 9. | |
| 13 | In the Execution log, copy the code after `Deployer secret:`. Paste it in your note as **DEPLOY_BRIDGE_SECRET**. | |
| 14 | Pick **testApiAccess** → **▶ Run**. | `OK — Apps Script API works` |
| 15 | **Deploy → New deployment → ⚙️ → Web app**, with **Execute as: Me** and **Who has access: Anyone** → **Deploy**. Copy the **Web app URL** into your note as **DEPLOY_BRIDGE_URL**. | |
>>>

### Turn A3 — 2c. Share the details with your agent (about 5 min)

Show the content below, then say "Tell me what your agent replied." **Stop and wait.**

>>>
**2c. Share the details with your agent**

1. In Antigravity, open the folder you'll use for Part 3 and start a new agent chat.
2. Copy the message below, fill in the 5 details from your note and your own Gmail address, and send it.

```
Here are my bridge details for this session. Keep them in this chat only:
don't write them into any file.

TEST_BRIDGE_URL:
TEST_BRIDGE_SECRET:
DEPLOY_BRIDGE_URL:
DEPLOY_BRIDGE_SECRET:
SCRIPT_ID:
TEST_EMAILS: yourname+t1@gmail.com, yourname+t2@gmail.com

Check both bridges: send a POST request with {"action": "check",
"secret": <its secret>} to each URL. Tell me in one line whether each
one worked. Do nothing else.
```

**What good looks like:** the agent reports that both bridges replied `ok`.

*Optional, for more experienced users:* instead of pasting, put the same six lines in a `.env` file in the project folder, add `.env` to `.gitignore`, and tell the agent to read the details from `.env`.
>>>

### Turn B — Support

Help only if asked. Common issues:

| Issue | Help |
|---|---|
| The agent's table is missing `setupTestBridge`, `setupBridge` or `testApiAccess`, or names them differently | Tell it: "Check both files against the contract and rename anything that doesn't match exactly." |
| A file in the prompt is missing, or the agent tried to deploy | Tell it: "Only write the files in bridge_files. Don't deploy anything." Then paste the prompt again. |
| `testApiAccess` doesn't log the OK line, or `release` fails at a step | The generated code may differ from the contract. Paste the error back to the agent in Antigravity and ask it to fix only that function, then paste the file into Apps Script again. |
| "Authorization required" keeps coming back | Run the function again and complete every screen, including **Advanced → Go to … (unsafe) → Allow**. |
| A file ended up as `test_bridge.gs.gs` | Rename it to `test_bridge` (click ⋮ next to the file → Rename). |
| `testApiAccess` fails with 403 "Apps Script API has not been used in project…" | The project isn't linked. Check 2b step 3 (API enabled) and step 9 (project **number**, not ID). Wait 2 minutes, then run it again. |
| "Change project" says the project is invalid | They copied the Project ID. Copy the all-digit **Project number** instead. |
| After creating the consent screen: "You haven't configured any OAuth clients" | Ignore it. No OAuth client is needed; Apps Script handles sign-in. Go to **Audience → Test users**. |
| The consent screen looks different from the steps | Google changes it often. The essentials: External, your email as the contact, and yourself as a test user. |
| The agent's check returns "Wrong or missing secret" | A secret was pasted with a space or into the wrong line. If they re-ran `setupTestBridge` or `setupBridge`, the secret changed: copy the newest one from the Execution log. |
| The agent's check returns an HTML page or a login page | "Who has access" isn't **Anyone**. Deploy → Manage deployments → ✏️ → set Anyone → Deploy. |
| Their work Google account blocks "Anyone" web apps | Use a personal Gmail account instead. |
| They're running the session in Claude chat, not Antigravity | Turn on **All domains** in Settings → Capabilities, then start a new chat. |

After Turn A3, when they confirm both bridges replied `ok`, go to Turn C.

### Turn C — Check

Ask one question with tappable options:

**"In Part 3, which bridge will the Tester use to check that the app works?"**
- The deploy bridge
- The test bridge ✅
- Both

If they pick another answer, explain in two lines: the deploy bridge only pushes new code; the test bridge is how agents look at the live sheet, form and inbox.

### Turn D — End

Respond in 2–3 lines. Key takeaways:
- **The bridges are the agents' hands and eyes.** One ships code, the other checks results.
- **Secrets are power.** Anyone with a URL and its secret can run code as you, so keep them in the chat or `.env`, never in shared files. You'll archive both deployments at the end of the session (Part 4).

Then say "🔴 We are now ending Part 2" and ask "Ready to begin Part 3? Type "yes" to continue."

### Facilitator notes for Part 2 (for you, not shown as-is)

- Timing: generating the files about 5–10 min, 2a about 15 min, 2b about 25 min, 2c about 5 min. The slowest step is the Cloud Console in 2b. To save time, send the file prompts and 2b as pre-work.
- **Generated files vary between runs.** The prompts pin every name, log line and action the steps and Part 3 rely on, but test a generated set end to end (2a → 2c → one Part 3 release) before each cohort. If a cohort is short on time or less technical, share a tested `session_5_files` folder and skip Turn A0b. The reference files from your survey-app build are a good tested set.
- The contract is also the harness for Part 3: the release refuses to drop `appsscript` or `test_bridge`, and `deleteTab` refuses `Sheet1`. Point this out if participants ask why the prompts are so specific.
- Naming: the session says **deploy bridge**, but the file is still called `deployer_bridge.gs` and its log line says `Deployer secret:`. The steps name both, so participants aren't confused.
- The deploy bridge updates the test bridge's existing deployment. The deployment ID is the part of `TEST_BRIDGE_URL` between `/s/` and `/exec`, so the test bridge must be deployed before Part 3 starts.
- Part 3's prompt reads the details from the chat (with `.env` as the optional route), using the same six names as the 2c message.
- Lessons from the pilot, now built into the steps: the "no OAuth clients" message is safe to ignore, and the script and sheet time zones should match the participant's location.

---

## Part 3: App building and testing loop

Runs in the **same Antigravity chat** where the participant shared their bridge details in 2c, so the agent already has them. Allow about 45–60 minutes: a 10–15 minute PM interview, then 20–40 minutes of loop.

### Turn A — Begin

Say "🟢 We are now beginning Part 3: App building and testing loop", then show:

| Step | What | Why |
|---|---|---|
| 1 | In the Antigravity chat from 2c, paste the **loop prompt** | The agent writes `build_and_test_loop.md`, turning the Session 1 brief into a four-agent build loop |
| 2 | Read `build_and_test_loop.md`. Find the four roles and the Rules section | These are the "roles + coordination" and the harness |
| 3 | Say "go", answer the PM's questions, read `spec.md`, and reply "approved" | You approve what gets built before any code is written |
| 4 | Watch the loop: release → test → feedback, up to 5 attempts | The Tester, not the Engineer, decides whether it works |
| 5 | Open your Google Sheet and do the one `[HUMAN]` check the loop asks for | Some things only a person can see, like the menu |

Then show the reassurance line, then the content below:

>>>
**Loop prompt**

```
Read this brief and remember. Do not do anything yet.

Brief (from Session 1): We need to send survey questions to our community
members mailing list to gather their responses. Build a simple app using
Google Sheet + Google Form + Apps Script that:
* generates a Google Form from the "survey" tab
* sends the form to all emails in the "mailing_list" tab
* stores responses in the "responses" tab

Now write build_and_test_loop.md that turns this brief into a working app
on my live Google Sheet, using four agents:

1. Product Manager: interviews me with 2–3 pointed questions per round,
   each with options and one marked (Recommended). Then saves spec.md, with
   an "Appendix: how we got here" listing every question, the options and
   my answer, and test.md, with one test per acceptance criterion, each
   checkable through the test bridge.
2. Software Engineer: writes code.gs from spec.md, including setupSheet()
   (creates the tabs with headers and sample rows), resetApp() (returns the
   sheet to a clean state and forgets the old form) and appVersion()
   (returns the attempt number). Every public function returns a small
   JSON result so it can run through the bridge. On later attempts, reads
   feedback.md and fixes only what failed.
3. Tester: runs every test in test.md on the live sheet through the test
   bridge, never by reading the code, and writes feedback.md with details
   for failed tests only.
4. Loop Engineer: starts only after I approve spec.md. Then loops
   Software Engineer → release → Tester until all tests pass or 5 attempts,
   and logs each attempt in loop_log.md. On success, tell me in 3 lines or
   fewer. After 5 failed attempts, stop and ask me whether to revise the
   spec, allow 5 more attempts, or stop.

Connection to my Google Workspace (set up in Part 2):
- Use the bridge details I shared earlier in this chat (or in .env, if I
  used that): TEST_BRIDGE_URL, TEST_BRIDGE_SECRET, DEPLOY_BRIDGE_URL,
  DEPLOY_BRIDGE_SECRET, SCRIPT_ID and TEST_EMAILS. Never hard-code them in
  a file or repeat them in chat.
- Write one small bridge.py wrapper that reads them from environment
  variables, and reuse it.
- Preflight before attempt 1: "check" on both bridges, and the deploy
  bridge's "getContent" with SCRIPT_ID. Stop and tell me if any fails.
- Release with the deploy bridge's "release" action: scriptId,
  deploymentId (the part of TEST_BRIDGE_URL between /s/ and /exec), files
  and description. Each release replaces every file in the project, so
  always send all three: appsscript and test_bridge (copied from the
  current project) and Code.
- After each release, poll run appVersion until it returns the new version
  on 3 calls in a row before testing. It can take up to 90 seconds.
- Test bridge actions: check, run (fn, args), listTabs, readTab, writeTab,
  deleteTab, formInfo, submitResponse, gmailSearch.

Rules:
- Only send emails to TEST_EMAILS. Never use a real mailing list.
- Every attempt starts with resetApp() then setupSheet(), so each test run
  starts from a known state. Never delete the tab named Sheet1.
- Only the agent that owns a file writes it; the others only read it.
- If a test can't be checked through the bridge (e.g. how the menu looks),
  mark it [HUMAN] and ask me once at the end.
- If a new permission is needed, stop and ask me to click Run → Authorize,
  rather than working around it.
- Never run setupTestBridge or setupBridge: they change the secrets.

Known pitfalls:
- Sheets turns text like "1-5" into a date. Format option columns as plain
  text and parse them defensively.
- A test that fails right after a release may be the old version still
  running. Confirm appVersion before blaming the code.
- A value read right after a function writes it can come back empty. End
  every function that writes to the sheet with SpreadsheetApp.flush().
- If this sheet was used before, the old code may already report "v1".
  Use version labels unique to this run (e.g. s5-v1, s5-v2).
- The bridges sometimes return a one-off HTML page instead of JSON. Retry
  a call up to 3 times before treating it as a failure.

Keep things simple and my cognitive load small. Show me
build_and_test_loop.md, then start the PM interview when I say go.
```
>>>

End with: "Tell me when the loop has finished, or come back if you're stuck." **Stop and wait.**

*In Claude chat:* after showing the loop prompt, run it yourself, create `build_and_test_loop.md`, present it, and go straight to step 2 (point out the four roles and the Rules section). Then run the PM interview with tappable options, and the loop itself, as the agents.

### Turn B — Support

Help only if asked. Common issues:

| Issue | Help |
|---|---|
| The agent starts building straight after the prompt | Tell it: "Stop. Show me build_and_test_loop.md first, and wait for go." |
| Unsure how to answer a PM question | Pick the **(Recommended)** option. It's chosen to keep v0 simple. |
| They want to pause or stop the loop | Before approval: just don't reply "approved"; nothing runs. During the loop: click stop in Antigravity. Either way, archiving both deployments (Part 4 cleanup) guarantees nothing can act on the sheet. |
| Preflight fails | Go back to 2c: the agent should get `ok` from both bridges. Check for a mistyped secret, or an archived deployment. |
| "Authorization required" or a permission error mid-loop | Open the sheet's Apps Script, pick any small function (e.g. `appVersion`), click **Run**, and allow. Then tell the agent "done". Don't run `setupTestBridge`. |
| The test bridge file disappeared, or the bridge stopped answering after a release | The release left out `test_bridge` or `appsscript`. Remind the agent: every release must send all three files. |
| Tests fail right after a release, and the agent starts "fixing" code that looks correct | Tell it: "Check appVersion first. The old version may still be live." |
| The loop escalates after 5 attempts | That's the stop rule working. Choose "5 more attempts" if the failures are shrinking, or "revise the spec" if a test looks wrong. |
| A test fails because a tab or header read back empty, but a re-check shows it's there | The function returned before its writes were visible. Tell the agent: "End every function that writes to the sheet with SpreadsheetApp.flush()." |
| Preflight or a test fails with an HTML page (e.g. HTTP 404) instead of JSON | Usually a one-off from Google. `bridge.py` should retry up to 3 times; if it still fails, check that the deployment isn't archived. |
| The agent is waiting forever for the new version, or tests run on old code that already says "v1" | The sheet was reused. Tell the agent to use labels unique to this run, such as `s5-v1`. |
| Survey emails land in their inbox | Expected. They go to their own `+t1`/`+t2` aliases. |
| A test is skipped because a form already exists | Fine on re-runs. `resetApp()` should prevent it; if not, tell the agent to make `resetApp()` forget the saved form. |

When they say the loop has finished, go to Turn C.

### Turn C — Check

Ask one question with tappable options:

**"Who decided that your app actually works?"**
- The Software Engineer, after reviewing its own code
- The Tester, by running test.md on your live sheet ✅
- The Product Manager, by approving the spec

If they pick another answer, explain in two lines: the agent that writes the code never grades it. A separate Tester checks the real sheet, form and inbox, which is what makes the result trustworthy.

### Turn D — End

Respond in 2–3 lines, drawing on their loop log. Key takeaways:
- **Multi-agent = roles + coordination.** Each agent owns one file, and the Loop Engineer passes work between them.
- **The harness makes it reliable.** The rules and known pitfalls in the prompt come from failures in earlier runs. Each lesson becomes a rule, so the next loop doesn't repeat it.

Then say "🔴 We are now ending Part 3" and ask "Ready to begin Part 4? Type "yes" to continue."

### Facilitator notes for Part 3 (for you, not shown as-is)

Reference run (the survey-app build this loop came from): **all 11 automated tests passed on attempt 3 of 5**.

| Attempt | Result | What happened |
|---|---|---|
| 1 | 4/11 | Sheets turned the scale option `1-5` into a date, so no form could be built |
| 2 | 3/11 | The fix worked, but the edit broke `setupSheet` (a regression the Tester caught) |
| 3 | 11/11 | Fixed. The first test run hit stale code (release lag); the re-test passed |

- **Session run (28 Sep 2026, in Claude chat, with the pitfalls in the prompt): SUCCESS, 10/10 on attempt 2 of 5.** Attempt 1 scored 9/10: T1 read the `responses` header back empty straight after `setupSheet`, though a re-check showed it was there. The fix was `SpreadsheetApp.flush()` before returning, and it is now a known pitfall. The same run also hit a one-off HTML 404 on `getContent` during preflight (now a retry pitfall) and old code already reporting `v1` on the reused sheet (now the unique-label pitfall). T10 (the menu) was confirmed by eye. The PM interview took 3 rounds, all Recommended.
- The original reference run's attempts 1 and 3 are "Known pitfalls" in the prompt, and the session run confirms participants' runs pass sooner. That's a good teaching moment: **the harness grew from real failures.** To show the loop recovering live, run a demo without the "Known pitfalls" block, then reveal it as the harness fix.
- **Session pilot (28 Sep 2026)** stopped at the approval gate. The PM interview took 3 rounds (all Recommended) and produced spec v0 with 10 ACs (AC10, the menu, as the only `[HUMAN]` check). The spec was never approved, so nothing was released or sent. Use it as a teaching point: **a human gate is also a stop criterion.** Nothing gets built without a human yes.
- The `[HUMAN]` check is usually the **Survey App** menu: reload the sheet and look for it. A different interview can produce a different `[HUMAN]` test.
- The PM interview is the slowest part. Encourage "pick Recommended" to keep it to 3–4 rounds.
- If the loop escalates, the most common real cause is a permission needing Authorize, not bad code.

---

## Part 4: Crystallized learnings

Allow about 15–20 minutes. Runs in this chat, plus one prompt in a **new** Antigravity chat.

### Turn A — Begin

Say "🟢 We are now beginning Part 4: Crystallized learnings", then show:

| Step | What | Why |
|---|---|---|
| 1 | Read the **three ideas** table and match each idea to what you did today | Gives names to what you already did |
| 2 | Paste the **design prompt** into a new Antigravity chat and answer its questions | Turns the three ideas into a plan for your own problem |
| 3 | Read `my_agent_design.md` and check it has all three sections | A design without a stop rule or a separate checker isn't ready to build |
| 4 | Clean up: archive both bridge deployments from Part 2 | Anyone with a URL and its secret can run code as you |

Then show the reassurance line, then the content below:

>>>
**The three ideas**

| Idea | In one line | Where you saw it today | Question to ask of any agent |
|---|---|---|---|
| **Loop** | Goal + stop criteria | Part 1: a MAPE target, a 5-attempt budget, and a stop script the agent couldn't overrule | What's the scoreboard, and what stops it? |
| **Multi-agent orchestration** | Roles + coordination | Part 3: PM, Engineer, Tester and Loop Engineer, each owning one file | Who does the work, and who checks it? |
| **Harness** | Rules that make an agent work reliably | Parts 1–3: the overfit and hypothesis rules, bridges and secrets, test emails only, the approval gate, known pitfalls | Which past failure has become a rule? |

**How they fit together:** the harness is the environment, a loop runs inside it, and orchestration coordinates several loops. In one sentence: *an agent you can trust has a goal, a stop rule it can't overrule, and a set of rules it works inside.*

**Design prompt**

```
Help me design an agentic system for a real problem at my work. Do not
build anything.

Interview me with 2–3 pointed questions per round, each with options and
one marked (Recommended). Aim for 3 rounds. Then write my_agent_design.md
with three sections:

1. Loop: the goal, the metric or tests that show progress, the stop
   criteria (target reached, max attempts, or a human gate), and what
   happens when it stops without reaching the goal.
2. Roles: the fewest agents needed, what each one owns and reads, and
   which agent checks the work. The agent that does the work must never
   be the one that grades it.
3. Harness: 3–5 rules that keep it safe and reliable, including where a
   human must approve, what the agents may never touch, and how secrets
   stay out of files.

End with the one piece I should build first as v0. Keep it to one page
and my cognitive load small.
```

**Cleanup (do this before you leave)**

In each Apps Script project from Part 2 (your sheet's `Survey app` script and the `Deploy bridge` project), go to **Deploy → Manage deployments**, select the web app and click **Archive**. The URLs stop working, and the secrets become useless.
>>>

End with: "Tell me when `my_agent_design.md` is ready and your bridges are archived, or come back if you're stuck." **Stop and wait.**

### Turn B — Support

Help only if asked. Common issues:

| Issue | Help |
|---|---|
| Can't think of a problem | Reuse a friction from your Session 2 or 4 discovery, or pick a weekly report you build by hand. |
| No clear number to measure | Use pass/fail tests instead, as `test.md` did in Part 3. A checklist is a scoreboard too. |
| The design has 4+ agents | Ask the agent: "Which roles can we merge?" A doer and a separate checker are often enough for v0. |
| Can't find Manage deployments | Open the script from the sheet (**Extensions → Apps Script**), then use the blue **Deploy** button at top right. Repeat in the `Deploy bridge` project at script.google.com. |
| Want to keep using the bridges later | Archive them now anyway. Next time, create a new deployment and run `setupTestBridge` / `setupBridge` once to get fresh secrets. |

When they say they're done, go to Turn C.

### Turn C — Check

Ask one question with tappable options:

**"In Part 1, the loop stopped at about 15% MAPE against a 5% target. Was that a failure of the loop?"**
- Yes, it missed the target
- No, the stop rule worked and it reported honestly ✅
- Yes, it should have kept trying until it hit 5%

If they pick another answer, explain in two lines: a loop succeeds when it stops for the right reason and tells you the truth. Missing the target with the data available is a finding, not a failure; a loop that never stops is the real failure.

### Turn D — End

Respond in 2–3 lines, drawing on their `my_agent_design.md`: name their goal, their checker role, and one harness rule they wrote.

Then say "🔴 We are now ending Part 4", show the artifacts table below, and close with:
- **Your next step (2–4 weeks):** build the v0 from `my_agent_design.md`, run it on real work, and keep a short failure log. Every failure you fix should become a rule in your harness. Bring it back for show-and-tell.
- Thank them for coming.

### Facilitator notes for Part 4 (for you, not shown as-is)

- Map the three ideas back to the participant's own runs rather than the reference tables; their numbers make it stick. If their Part 1 run ended at a different MAPE, adjust the number in the check question.
- The most common design mistake is letting the doer grade itself. Point back to the Part 3 check: the Tester, not the Engineer, decided whether the app worked.
- Model the cleanup yourself on screen. In the pilot, bridge secrets were pasted into chats, which is exactly why the deployments should be archived after the session.
- If time is short, skip the design prompt and assign it as the first task of the 2–4 week challenge. Keep the cleanup step.

---

## End of session: artifacts

| File | From | What it is |
|---|---|---|
| `data.csv` | Part 1 | California housing data |
| `training_loop.md` | Part 1 | The loop plan, with overfit and hypothesis rules |
| `train.py`, `check_stop.py`, `analyze.py` | Part 1 | Training script, stop rule, error analysis |
| `experiments.csv` | Part 1 | One row per attempt, with hypothesis, overfit gap and whether it was supported |
| `results.md` | Part 1 | Final report |
| `best_model.pkl` | Part 1 | Best model |
| `bridge_files/` (`sheet_appsscript.json`, `test_bridge.gs`, `deployer_appsscript.json`, `deployer_bridge.gs`) | Part 2 | The generated bridge code |
| `Survey app test` sheet, `Survey app` and `Deploy bridge` scripts | Part 2 | Your live sheet and the two bridges (web apps archived at the end) |
| `build_and_test_loop.md` | Part 3 | The four-agent loop and its rules |
| `spec.md`, `test.md` | Part 3 | The approved spec (with interview appendix) and acceptance tests |
| `code.gs`, `feedback.md`, `loop_log.md` | Part 3 | The final app, the last test results, and one entry per attempt |
| `my_agent_design.md` | Part 4 | Your own loop, roles and harness, with a v0 to build first |
