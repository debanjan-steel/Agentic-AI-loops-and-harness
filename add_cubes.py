import json
import time
import urllib.request
import urllib.error

env = {}
with open('.env') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, v = line.split('=', 1)
            env[k.strip()] = v.strip()

url = env.get('ANOTHER_APP_TEST_BRIDGE_URL') or env.get('TEST_BRIDGE_URL')
secret = env.get('ANOTHER_APP_TEST_BRIDGE_SECRET') or env.get('TEST_BRIDGE_SECRET')

def call_bridge(payload, retries=3):
    data = json.dumps(payload).encode('utf-8')
    for attempt in range(retries):
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=20) as res:
                text = res.read().decode('utf-8')
                try:
                    return json.loads(text)
                except Exception:
                    time.sleep(2)
        except Exception as e:
            time.sleep(2)
    return None

# 1. Read Numbers tab
read_res = call_bridge({'action': 'readTab', 'secret': secret, 'tab': 'Numbers'})
if not read_res or not read_res.get('ok'):
    print("Failed to read Numbers tab:", read_res)
    exit(1)

data = read_res.get('values', [])
print("Read numbers:", data)

# 2. Compute cubes
output = []
for i, row in enumerate(data):
    new_row = []
    for cell in row:
        if i == 0 and not str(cell).isdigit():
            new_row.append(str(cell) + ' Cubed')
        else:
            try:
                val = float(cell)
                cubed = val ** 3
                new_row.append(str(int(cubed) if cubed.is_integer() else cubed))
            except ValueError:
                new_row.append(str(cell))
    output.append(new_row)

print("Cubed data:", output)

# 3. Write Cubes tab
write_res = call_bridge({'action': 'writeTab', 'secret': secret, 'tab': 'Cubes', 'values': output})
print("Write Cubes tab result:", write_res)
