"""Diagnose the OpenRouter setup: is the key live, what models can it see, does a call work?

Uses only the standard library, so it runs regardless of what is installed.

Run with:  python check_key.py
"""

import json
import urllib.error
import urllib.request

from config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, OPENROUTER_MODEL

TIMEOUT = 60


def call(url, body=None):
    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=body, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as exc:
        return exc.code, b""
    except Exception:
        return None, None


print("OpenRouter key configured: yes")

status, _ = call(f"{OPENROUTER_BASE_URL}/key")
print(f"[1] auth      {OPENROUTER_BASE_URL}/key  -> HTTP {status}")
print()

if status != 200:
    print("OpenRouter did not accept the configured key; response content is suppressed.")
    print("Check OPENROUTER_API_KEY in your local .env file.")
    raise SystemExit(1)

status, body = call(f"{OPENROUTER_BASE_URL}/models")
print(f"[2] catalogue {OPENROUTER_BASE_URL}/models  -> HTTP {status}")

if status == 200:
    try:
        ids = [model["id"] for model in json.loads(body)["data"]]
        present = OPENROUTER_MODEL in ids
        print(f"    {len(ids)} models visible; configured model present: {present}")
    except (KeyError, TypeError, ValueError):
        print("    Provider response could not be parsed; response content is suppressed.")
print()

payload = json.dumps(
    {
        "model": OPENROUTER_MODEL,
        "messages": [{"role": "user", "content": "Reply with the single word OK."}],
    }
).encode()

status, _ = call(f"{OPENROUTER_BASE_URL}/chat/completions", body=payload)
print(f"[3] completion {OPENROUTER_MODEL!r} -> HTTP {status}")

if status == 200:
    print("    completion probe succeeded; response content is suppressed.")
    print("All three checks passed. Restart Streamlit to use the updated configuration.")
else:
    print("    Completion probe failed; provider response content is suppressed.")
