import urllib.request
import urllib.error

url = "http://127.0.0.1:5000/api/data/burst-test"
headers = {"X-API-Key": "live-demo-key-1"}

print("=== FIRING 7 RAPID REQUESTS TO BURST ENDPOINT (LIMIT 5) ===")
for i in range(1, 8):
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            remaining = resp.headers.get("X-RateLimit-Remaining")
            print(f"Request #{i}: 200 OK — Remaining Tokens: {remaining}")
    except urllib.error.HTTPError as e:
        retry_after = e.headers.get("Retry-After")
        print(f"Request #{i}: {e.code} Too Many Requests — Retry After: {retry_after} seconds")
