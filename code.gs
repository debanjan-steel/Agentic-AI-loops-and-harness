/**
 * Community Survey Application (Session 5 - Attempt 2)
 */

function appVersion() {
  return "s5-v2";
}

function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu("Survey App")
    .addItem("Setup Sheet", "setupSheet")
    .addItem("Generate Form", "generateForm")
    .addItem("Send Surveys", "sendSurveys")
    .addItem("Sync Responses", "syncResponses")
    .addItem("Reset App", "resetApp")
    .addToUi();

  ui.createMenu("Number Tools")
    .addItem("Square the number", "squareNumbers")
    .addToUi();
}

function squareNumbers() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const numSheet = ss.getSheetByName("Numbers");
  if (!numSheet) {
    return { ok: false, error: "Numbers tab not found" };
  }

  const data = numSheet.getDataRange().getValues();
  if (!data || data.length === 0) {
    return { ok: false, error: "No data in Numbers tab" };
  }

  let sqSheet = ss.getSheetByName("Squares");
  if (!sqSheet) {
    sqSheet = ss.insertSheet("Squares");
  }
  sqSheet.clear();

  const output = data.map((row, rIdx) => {
    return row.map((cell) => {
      if (rIdx === 0 && isNaN(cell)) {
        return String(cell) + " Squared";
      }
      const val = Number(cell);
      if (!isNaN(val) && cell !== "" && cell !== null) {
        return val * val;
      }
      return cell;
    });
  });

  sqSheet.getRange(1, 1, output.length, output[0].length).setValues(output);
  SpreadsheetApp.flush();
  return { ok: true, rows: output.length };
}

function resetApp() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const tabsToDelete = ["survey", "mailing_list", "responses"];
  tabsToDelete.forEach(tabName => {
    const sheet = ss.getSheetByName(tabName);
    if (sheet) {
      if (tabName !== "Sheet1") {
        ss.deleteSheet(sheet);
      }
    }
  });

  // Ensure Sheet1 exists
  if (!ss.getSheetByName("Sheet1")) {
    ss.insertSheet("Sheet1");
  }

  // Clear stored form properties
  PropertiesService.getScriptProperties().deleteProperty("SURVEY_FORM_URL");
  PropertiesService.getScriptProperties().deleteProperty("SURVEY_FORM_PUBLISHED_URL");
  PropertiesService.getScriptProperties().deleteProperty("SURVEY_FORM_ID");

  SpreadsheetApp.flush();
  return { ok: true, reset: true };
}

function setupSheet() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();

  // 1. survey tab
  let surveySheet = ss.getSheetByName("survey");
  if (!surveySheet) {
    surveySheet = ss.insertSheet("survey");
  }
  surveySheet.clear();
  const surveyHeaders = ["Title", "Type", "Required", "Options"];
  const surveyRows = [
    surveyHeaders,
    ["Your Name", "Text", "TRUE", ""],
    ["Community Role", "Multiple Choice", "TRUE", "Student, Educator, Professional, Enthusiast"],
    ["Overall Satisfaction", "Scale", "TRUE", "1-5"]
  ];
  surveySheet.getRange(1, 1, surveyRows.length, surveyHeaders.length)
    .setNumberFormat("@")
    .setValues(surveyRows);

  // 2. mailing_list tab
  let mailSheet = ss.getSheetByName("mailing_list");
  if (!mailSheet) {
    mailSheet = ss.insertSheet("mailing_list");
  }
  mailSheet.clear();
  const mailHeaders = ["Name", "Email", "Status"];
  const mailRows = [
    mailHeaders,
    ["Debanjan", "debanjan17052002@gmail.com", "Pending"]
  ];
  mailSheet.getRange(1, 1, mailRows.length, mailHeaders.length)
    .setNumberFormat("@")
    .setValues(mailRows);

  // 3. responses tab
  let respSheet = ss.getSheetByName("responses");
  if (!respSheet) {
    respSheet = ss.insertSheet("responses");
  }
  respSheet.clear();
  const respHeaders = ["Timestamp", "Your Name", "Community Role", "Overall Satisfaction"];
  respSheet.getRange(1, 1, 1, respHeaders.length)
    .setNumberFormat("@")
    .setValues([respHeaders]);

  SpreadsheetApp.flush();
  return { ok: true, setup: true };
}

function generateForm() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const surveySheet = ss.getSheetByName("survey");
  if (!surveySheet) {
    return { ok: false, error: "survey tab missing" };
  }

  const data = surveySheet.getDataRange().getDisplayValues();
  if (data.length <= 1) {
    return { ok: false, error: "survey tab has no questions" };
  }

  const form = FormApp.create("Community Survey");
  
  for (let i = 1; i < data.length; i++) {
    const title = data[i][0];
    const type = data[i][1];
    const required = String(data[i][2]).toUpperCase() === "TRUE";
    const optionsRaw = data[i][3];

    if (!title) continue;

    if (type === "Text") {
      const item = form.addTextItem().setTitle(title).setRequired(required);
    } else if (type === "Multiple Choice") {
      const item = form.addMultipleChoiceItem().setTitle(title).setRequired(required);
      const choices = optionsRaw.split(",").map(s => s.trim()).filter(Boolean);
      if (choices.length > 0) {
        item.setChoiceValues(choices);
      }
    } else if (type === "Scale") {
      const item = form.addScaleItem().setTitle(title).setRequired(required);
      item.setBounds(1, 5);
    }
  }

  // Use editUrl for API operations (formInfo, submitResponse) and publishedUrl for respondents
  const editUrl = form.getEditUrl();
  const publishedUrl = form.getPublishedUrl();
  const formId = form.getId();

  PropertiesService.getScriptProperties().setProperties({
    "SURVEY_FORM_URL": editUrl,
    "SURVEY_FORM_PUBLISHED_URL": publishedUrl,
    "SURVEY_FORM_ID": formId
  });

  return { ok: true, formUrl: editUrl, publishedUrl: publishedUrl, formId: formId };
}

function sendSurveys() {
  const publishedUrl = PropertiesService.getScriptProperties().getProperty("SURVEY_FORM_PUBLISHED_URL")
                    || PropertiesService.getScriptProperties().getProperty("SURVEY_FORM_URL");
  if (!publishedUrl) {
    return { ok: false, error: "Form has not been generated yet" };
  }

  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const mailSheet = ss.getSheetByName("mailing_list");
  if (!mailSheet) {
    return { ok: false, error: "mailing_list tab missing" };
  }

  const values = mailSheet.getDataRange().getDisplayValues();
  if (values.length <= 1) {
    return { ok: true, sentCount: 0 };
  }

  let sentCount = 0;
  for (let i = 1; i < values.length; i++) {
    const name = values[i][0];
    const email = values[i][1];
    if (email && email.includes("@")) {
      MailApp.sendEmail({
        to: email,
        subject: "Community Survey",
        body: "Hello " + name + ",\n\nPlease fill out our community survey here:\n" + publishedUrl + "\n\nThank you!"
      });
      mailSheet.getRange(i + 1, 3).setValue("Sent");
      sentCount++;
    }
  }

  SpreadsheetApp.flush();
  return { ok: true, sentCount: sentCount };
}

function syncResponses() {
  const formId = PropertiesService.getScriptProperties().getProperty("SURVEY_FORM_ID");
  if (!formId) {
    return { ok: false, error: "Form ID not found" };
  }

  const form = FormApp.openById(formId);
  const formResponses = form.getResponses();
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const respSheet = ss.getSheetByName("responses");
  if (!respSheet) {
    return { ok: false, error: "responses tab missing" };
  }

  // Clear existing response rows (keep header row)
  const lastRow = respSheet.getLastRow();
  if (lastRow > 1) {
    respSheet.getRange(2, 1, lastRow - 1, 4).clearContent();
  }

  const rowsToAdd = [];
  formResponses.forEach(fr => {
    const timestamp = fr.getTimestamp();
    const itemResponses = fr.getItemResponses();
    let name = "";
    let role = "";
    let rating = "";

    itemResponses.forEach(ir => {
      const qTitle = ir.getItem().getTitle();
      const answer = ir.getResponse();
      if (qTitle === "Your Name") {
        name = answer;
      } else if (qTitle === "Community Role") {
        role = answer;
      } else if (qTitle === "Overall Satisfaction") {
        rating = answer;
      }
    });

    rowsToAdd.push([timestamp, name, role, rating]);
  });

  if (rowsToAdd.length > 0) {
    respSheet.getRange(2, 1, rowsToAdd.length, 4).setValues(rowsToAdd);
  }

  SpreadsheetApp.flush();
  return { ok: true, responseCount: rowsToAdd.length };
}
