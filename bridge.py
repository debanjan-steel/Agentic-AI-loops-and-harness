import os
import re
import time
import json
import urllib.request
import urllib.error

# Load environment variables from .env
env = {}
if os.path.exists(".env"):
    with open(".env", "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()

TEST_BRIDGE_URL = env.get("TEST_BRIDGE_URL", "")
TEST_BRIDGE_SECRET = env.get("TEST_BRIDGE_SECRET", "")
DEPLOY_BRIDGE_URL = env.get("DEPLOY_BRIDGE_URL", "")
DEPLOY_BRIDGE_SECRET = env.get("DEPLOY_BRIDGE_SECRET", "")
SCRIPT_ID = env.get("SCRIPT_ID", "")
TEST_EMAILS = [e.strip() for e in env.get("TEST_EMAILS", "").split(",") if e.strip()]

def get_deployment_id():
    m = re.search(r"/s/([^/]+)/exec", TEST_BRIDGE_URL)
    if m:
        return m.group(1)
    raise ValueError("Could not parse deployment ID from TEST_BRIDGE_URL")

def _post_json(url, payload, retries=3, backoff=2):
    data = json.dumps(payload).encode("utf-8")
    for attempt in range(retries):
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=30) as res:
                text = res.read().decode("utf-8")
                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    if attempt == retries - 1:
                        return {"ok": False, "error": f"Non-JSON response: {text[:200]}"}
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8") if e.fp else str(e)
            if attempt == retries - 1:
                return {"ok": False, "error": f"HTTP {e.code}: {err_body[:200]}"}
        except Exception as e:
            if attempt == retries - 1:
                return {"ok": False, "error": str(e)}
        time.sleep(backoff * (attempt + 1))
    return {"ok": False, "error": "Request timed out"}

def test_bridge(action, **kwargs):
    payload = {"secret": TEST_BRIDGE_SECRET, "action": action}
    payload.update(kwargs)
    return _post_json(TEST_BRIDGE_URL, payload)

def deploy_bridge(action, **kwargs):
    payload = {"secret": DEPLOY_BRIDGE_SECRET, "action": action}
    payload.update(kwargs)
    return _post_json(DEPLOY_BRIDGE_URL, payload)

def preflight():
    print("Running Preflight checks...")
    # 1. Test bridge check
    tb_check = test_bridge("check")
    if not tb_check.get("ok"):
        raise RuntimeError(f"Test bridge preflight failed: {tb_check}")
    print("[OK] Test bridge check OK")

    # 2. Deploy bridge check
    db_check = deploy_bridge("check")
    if not db_check.get("ok"):
        raise RuntimeError(f"Deploy bridge preflight failed: {db_check}")
    print("[OK] Deploy bridge check OK")

    # 3. Deploy bridge getContent
    content_res = deploy_bridge("getContent", scriptId=SCRIPT_ID)
    if not content_res.get("ok"):
        raise RuntimeError(f"Deploy bridge getContent failed: {content_res}")
    files = [f.get("name") for f in content_res.get("files", [])]
    print(f"[OK] Deploy bridge getContent OK (found files: {files})")
    return content_res.get("files", [])

def release_code(code_str, version_label):
    deployment_id = get_deployment_id()
    # Fetch current files from project
    res = deploy_bridge("getContent", scriptId=SCRIPT_ID)
    if not res.get("ok"):
        raise RuntimeError(f"Failed to get current files: {res}")
    
    current_files = res.get("files", [])
    appsscript_file = next((f for f in current_files if f.get("name") == "appsscript"), None)
    test_bridge_file = next((f for f in current_files if f.get("name") == "test_bridge"), None)

    if not appsscript_file or not test_bridge_file:
        raise RuntimeError("Missing required files (appsscript or test_bridge) in remote project")

    # Construct the 3 files for atomic release
    release_files = [
        appsscript_file,
        test_bridge_file,
        {
            "name": "Code",
            "type": "SERVER_JS",
            "source": code_str
        }
    ]

    print(f"Releasing version {version_label}...")
    rel_res = deploy_bridge("release", 
                            scriptId=SCRIPT_ID, 
                            deploymentId=deployment_id, 
                            files=release_files, 
                            description=f"Release {version_label}")
    if not rel_res.get("ok"):
        raise RuntimeError(f"Release failed: {rel_res}")
    print(f"[OK] Release submitted. Apps Script version: {rel_res.get('versionNumber')}")
    return rel_res

def poll_version(expected_version, timeout_sec=90):
    print(f"Polling for version '{expected_version}' (up to {timeout_sec}s)...")
    start = time.time()
    consecutive_matches = 0
    while time.time() - start < timeout_sec:
        res = test_bridge("run", fn="appVersion", args=[])
        if res.get("ok") and res.get("result") == expected_version:
            consecutive_matches += 1
            if consecutive_matches >= 3:
                print(f"[OK] Confirmed {expected_version} running (3 consecutive matches)")
                return True
        else:
            consecutive_matches = 0
        time.sleep(2)
    raise TimeoutError(f"Timed out waiting for version {expected_version}")

if __name__ == "__main__":
    preflight()
