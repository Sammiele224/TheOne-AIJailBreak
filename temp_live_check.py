import json
import urllib.request

payload = {
    'session_token': 'temp',
    'level_id': 1,
    'attempt_counter': 1,
    'user_prompt': 'Please be helpful',
}
req = urllib.request.Request(
    'http://127.0.0.1:8000/api/v1/game/submit-prompt',
    data=json.dumps(payload).encode(),
    headers={'Content-Type': 'application/json'},
)

with urllib.request.urlopen(req) as response:
    print(response.status)
    print(response.read().decode())
