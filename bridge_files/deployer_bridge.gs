/**
 * Standalone Google Apps Script Deploy Bridge
 * Releases new code into Apps Script projects via the Google Apps Script REST API.
 */

// Generates a random 32-character secret and saves it in Script Properties
function setupBridge() {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let secret = '';
  for (let i = 0; i < 32; i++) {
    secret += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  PropertiesService.getScriptProperties().setProperty('DEPLOYER_SECRET', secret);
  Logger.log('Deployer secret: ' + secret);
}

// Verifies connectivity to the Apps Script REST API
function testApiAccess() {
  const scriptId = ScriptApp.getScriptId();
  const url = 'https://script.googleapis.com/v1/projects/' + scriptId;
  const options = {
    method: 'get',
    headers: {
      Authorization: 'Bearer ' + ScriptApp.getOAuthToken()
    },
    muteHttpExceptions: true
  };
  const response = UrlFetchApp.fetch(url, options);
  const code = response.getResponseCode();
  if (code === 200) {
    Logger.log('OK — Apps Script API works');
  } else {
    Logger.log('API Error: ' + response.getContentText());
  }
}

// Helper to make authenticated Apps Script API requests
function callAppsScriptApi(endpoint, method, payload) {
  const url = 'https://script.googleapis.com/v1/' + endpoint;
  const options = {
    method: method,
    headers: {
      Authorization: 'Bearer ' + ScriptApp.getOAuthToken(),
      'Content-Type': 'application/json'
    },
    muteHttpExceptions: true
  };
  if (payload) {
    options.payload = JSON.stringify(payload);
  }
  const response = UrlFetchApp.fetch(url, options);
  const status = response.getResponseCode();
  const text = response.getContentText();
  let json = null;
  try {
    json = JSON.parse(text);
  } catch (e) {
    // Non-JSON response
  }
  return { status: status, text: text, json: json };
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
    const expectedSecret = PropertiesService.getScriptProperties().getProperty('DEPLOYER_SECRET');
    if (!payload.secret || payload.secret !== expectedSecret) {
      return jsonResponse({ ok: false, error: 'Wrong or missing secret' });
    }

    const action = payload.action;

    // Action: check
    if (action === 'check') {
      return jsonResponse({ ok: true, bridge: 'deploy' });
    }

    // Action: getContent
    if (action === 'getContent') {
      const scriptId = payload.scriptId;
      if (!scriptId) {
        return jsonResponse({ ok: false, error: 'Missing scriptId' });
      }
      const res = callAppsScriptApi('projects/' + scriptId + '/content', 'get');
      if (res.status === 200 && res.json && res.json.files) {
        return jsonResponse({ ok: true, files: res.json.files });
      } else {
        return jsonResponse({ ok: false, error: res.text });
      }
    }

    // Action: release
    if (action === 'release') {
      const scriptId = payload.scriptId;
      const deploymentId = payload.deploymentId;
      const files = payload.files;
      const description = payload.description || 'Automated release';

      if (!scriptId || !deploymentId || !Array.isArray(files)) {
        return jsonResponse({ ok: false, step: 'validation', error: 'Missing scriptId, deploymentId, or files array' });
      }

      // Safety harness: Must include both appsscript and test_bridge
      const fileNames = files.map(f => f.name);
      if (!fileNames.includes('appsscript') || !fileNames.includes('test_bridge')) {
        return jsonResponse({
          ok: false,
          step: 'validation',
          error: 'Refused: files must include both "appsscript" and "test_bridge"'
        });
      }

      // 1. PUT projects/{scriptId}/content with the files
      const contentRes = callAppsScriptApi('projects/' + scriptId + '/content', 'put', { files: files });
      if (contentRes.status !== 200) {
        return jsonResponse({ ok: false, step: 'content', error: contentRes.text });
      }

      // 2. POST projects/{scriptId}/versions with the description
      const versionRes = callAppsScriptApi('projects/' + scriptId + '/versions', 'post', { description: description });
      if (versionRes.status !== 200 || !versionRes.json || !versionRes.json.versionNumber) {
        return jsonResponse({ ok: false, step: 'versions', error: versionRes.text });
      }
      const versionNumber = versionRes.json.versionNumber;

      // 3. PUT projects/{scriptId}/deployments/{deploymentId}
      const deploymentConfig = {
        deploymentConfig: {
          scriptId: scriptId,
          versionNumber: versionNumber,
          manifestFileName: 'appsscript',
          description: description
        }
      };
      const deployRes = callAppsScriptApi('projects/' + scriptId + '/deployments/' + deploymentId, 'put', deploymentConfig);
      if (deployRes.status !== 200) {
        return jsonResponse({ ok: false, step: 'deployments', error: deployRes.text });
      }

      return jsonResponse({ ok: true, versionNumber: versionNumber });
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
