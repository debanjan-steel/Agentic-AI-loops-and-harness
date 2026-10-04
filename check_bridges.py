import json
import urllib.request
import os

env = {}
with open('.env') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, v = line.split('=', 1)
            env[k.strip()] = v.strip()

def test_bridge(name, url, secret):
    if not url or not secret:
        return f"Missing url or secret for {name}"
    data = json.dumps({'action': 'check', 'secret': secret}).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=15) as res:
            return res.read().decode('utf-8')
    except Exception as e:
        return f"ERROR: {e}"

test_res = test_bridge('test', env.get('TEST_BRIDGE_URL'), env.get('TEST_BRIDGE_SECRET'))
deploy_res = test_bridge('deploy', env.get('DEPLOY_BRIDGE_URL'), env.get('DEPLOY_BRIDGE_SECRET'))

print("TEST_BRIDGE:", test_res)
print("DEPLOY_BRIDGE:", deploy_res)
