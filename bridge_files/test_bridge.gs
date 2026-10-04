/**
 * Google Apps Script Test Bridge
 * Provides HTTPS access for agents to inspect sheets, forms, gmail, and invoke app functions.
 */

// Generates a random 32-character secret and saves it in Script Properties
function setupTestBridge() {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let secret = '';
  for (let i = 0; i < 32; i++) {
    secret += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  PropertiesService.getScriptProperties().setProperty('TEST_BRIDGE_SECRET', secret);
  Logger.log('Test bridge secret: ' + secret);
}

// HTTP POST handler
function doPost(e) {
  try {
    if (!e || !e.postData || !e.postData.contents) {
      return jsonResponse({ ok: false, error: 'No payload provided' });
    }

    let payload;
    try {
      payload = JSON.parse(e.postData.contents);
    } catch (parseErr) {
      return jsonResponse({ ok: false, error: 'Malformed JSON payload' });
    }

    // Secret verification
    const expectedSecret = PropertiesService.getScriptProperties().getProperty('TEST_BRIDGE_SECRET');
    if (!payload.secret || payload.secret !== expectedSecret) {
      return jsonResponse({ ok: false, error: 'Wrong or missing secret' });
    }

    const action = payload.action;

    // Action: check
    if (action === 'check') {
      return jsonResponse({ ok: true, bridge: 'test' });
    }

    // Action: run
    if (action === 'run') {
      const fn = payload.fn;
      const args = payload.args || [];
      if (!fn || typeof fn !== 'string' || fn.startsWith('_') || fn === 'doPost' || fn === 'doGet' || fn === 'setupTestBridge') {
        return jsonResponse({ ok: false, error: 'Execution refused for forbidden or invalid function name' });
      }
      const targetFn = globalThis[fn];
      if (typeof targetFn !== 'function') {
        return jsonResponse({ ok: false, error: 'Function not found: ' + fn });
      }
      const result = Array.isArray(args) ? targetFn.apply(null, args) : targetFn.call(null, args);
      return jsonResponse({ ok: true, result: result !== undefined ? result : null });
    }

    // Action: listTabs
    if (action === 'listTabs') {
      const ss = SpreadsheetApp.getActiveSpreadsheet();
      const tabs = ss.getSheets().map(s => s.getName());
      return jsonResponse({ ok: true, tabs: tabs });
    }

    // Action: readTab
    if (action === 'readTab') {
      const tabName = payload.tab;
      const ss = SpreadsheetApp.getActiveSpreadsheet();
      const sheet = ss.getSheetByName(tabName);
      if (!sheet) {
        return jsonResponse({ ok: false, error: 'Tab not found: ' + tabName });
      }
      const values = sheet.getDataRange().getDisplayValues();
      return jsonResponse({ ok: true, values: values });
    }

    // Action: writeTab
    if (action === 'writeTab') {
      const tabName = payload.tab;
      const values = payload.values || [];
      const ss = SpreadsheetApp.getActiveSpreadsheet();
      let sheet = ss.getSheetByName(tabName);
      if (!sheet) {
        sheet = ss.insertSheet(tabName);
      }
      sheet.clear();
      if (values.length > 0 && values[0].length > 0) {
        const range = sheet.getRange(1, 1, values.length, values[0].length);
        range.setNumberFormat('@');
        range.setValues(values);
      }
      SpreadsheetApp.flush();
      return jsonResponse({ ok: true });
    }

    // Action: deleteTab
    if (action === 'deleteTab') {
      const tabName = payload.tab;
      if (tabName === 'Sheet1') {
        return jsonResponse({ ok: false, error: 'Refused: cannot delete Sheet1' });
      }
      const ss = SpreadsheetApp.getActiveSpreadsheet();
      const sheet = ss.getSheetByName(tabName);
      if (sheet) {
        ss.deleteSheet(sheet);
      }
      SpreadsheetApp.flush();
      return jsonResponse({ ok: true });
    }

    // Action: formInfo
    if (action === 'formInfo') {
      const formUrl = payload.formUrl;
      const form = FormApp.openByUrl(formUrl);
      const items = form.getItems().map(item => {
        const itemType = item.getType().toString();
        const info = {
          id: item.getId(),
          title: item.getTitle(),
          type: itemType,
          required: false
        };
        try {
          if (itemType === 'TEXT') {
            info.required = item.asTextItem().isRequired();
          } else if (itemType === 'PARAGRAPH_TEXT') {
            info.required = item.asParagraphTextItem().isRequired();
          } else if (itemType === 'MULTIPLE_CHOICE') {
            const mc = item.asMultipleChoiceItem();
            info.required = mc.isRequired();
            info.choices = mc.getChoices().map(c => c.getValue());
          } else if (itemType === 'CHECKBOX') {
            const cb = item.asCheckboxItem();
            info.required = cb.isRequired();
            info.choices = cb.getChoices().map(c => c.getValue());
          } else if (itemType === 'LIST') {
            const list = item.asListItem();
            info.required = list.isRequired();
            info.choices = list.getChoices().map(c => c.getValue());
          } else if (itemType === 'SCALE') {
            const scale = item.asScaleItem();
            info.required = scale.isRequired();
            info.lowerBound = scale.getLowerBound();
            info.upperBound = scale.getUpperBound();
          }
        } catch (e) {
          // Fallback if specific cast fails
        }
        return info;
      });

      return jsonResponse({
        ok: true,
        title: form.getTitle(),
        publishedUrl: form.getPublishedUrl(),
        responseCount: form.getResponses().length,
        items: items
      });
    }

    // Action: submitResponse
    if (action === 'submitResponse') {
      const formUrl = payload.formUrl;
      const answers = payload.answers || {};
      const form = FormApp.openByUrl(formUrl);
      const formResponse = form.createResponse();
      const items = form.getItems();

      for (let i = 0; i < items.length; i++) {
        const item = items[i];
        const title = item.getTitle();
        if (answers.hasOwnProperty(title)) {
          const val = answers[title];
          const type = item.getType();
          if (type === FormApp.ItemType.TEXT) {
            formResponse.withItemResponse(item.asTextItem().createResponse(String(val)));
          } else if (type === FormApp.ItemType.PARAGRAPH_TEXT) {
            formResponse.withItemResponse(item.asParagraphTextItem().createResponse(String(val)));
          } else if (type === FormApp.ItemType.MULTIPLE_CHOICE) {
            formResponse.withItemResponse(item.asMultipleChoiceItem().createResponse(String(val)));
          } else if (type === FormApp.ItemType.CHECKBOX) {
            const arrVal = Array.isArray(val) ? val.map(String) : [String(val)];
            formResponse.withItemResponse(item.asCheckboxItem().createResponse(arrVal));
          } else if (type === FormApp.ItemType.SCALE) {
            formResponse.withItemResponse(item.asScaleItem().createResponse(Number(val)));
          } else if (type === FormApp.ItemType.LIST) {
            formResponse.withItemResponse(item.asListItem().createResponse(String(val)));
          }
        }
      }
      formResponse.submit();
      return jsonResponse({ ok: true });
    }

    // Action: gmailSearch
    if (action === 'gmailSearch') {
      const query = payload.query || '';
      const threads = GmailApp.search(query, 0, 10);
      const results = threads.map(thread => {
        const msgs = thread.getMessages();
        const firstMsg = msgs.length > 0 ? msgs[0] : null;
        return {
          subject: thread.getFirstMessageSubject(),
          date: thread.getLastMessageDate().toISOString(),
          body: firstMsg ? firstMsg.getPlainBody().substring(0, 2000) : ''
        };
      });
      return jsonResponse({ ok: true, threads: results });
    }

    return jsonResponse({ ok: false, error: 'Unknown action: ' + action });

  } catch (err) {
    return jsonResponse({ ok: false, error: err.toString() });
  }
}

// Helper to format JSON HTTP response
function jsonResponse(data) {
  return ContentService
    .createTextOutput(JSON.stringify(data))
    .setMimeType(ContentService.MimeType.JSON);
}
