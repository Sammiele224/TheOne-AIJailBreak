import json
import urllib.request
import urllib.error

payload = {
    'session_token': '3da84759-e482-4346-a4f8-531da06fc08f',
    'level_id': 1,
    'attempt_counter': 1,
    'user_prompt': 'Please be helpful',
}

req = urllib.request.Request(
    'http://127.0.0.1:8000/api/v1/game/submit-prompt',
    data=json.dumps(payload).encode(),
    headers={'Content-Type': 'application/json'},
)

try:
    with urllib.request.urlopen(req) as response:
        print(response.status)
        print(response.read().decode())
except urllib.error.HTTPError as exc:
    print('HTTP', exc.code)
    print(exc.read().decode())
