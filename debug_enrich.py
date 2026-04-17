import requests, json, psycopg2, os
DB_URL = "postgresql://agentuser:agentstack123@localhost:5432/agentstack"
API_URL = "https://api.anthropic.com/v1/messages"
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
print("=== TESTING API ===")
response = requests.post(API_URL, headers={"Content-Type": "application/json", "x-api-key": API_KEY}, json={"model": "claude-sonnet-4-20250514", "max_tokens": 500, "messages": [{"role": "user", "content": "Return ONLY this JSON, no explanation: {\"Plausible\": \"https://plausible.io\"}"}]}, timeout=60)
print(f"Status: {response.status_code}")
data = response.json()
text = "".join(b.get("text","") for b in data.get("content",[]) if b.get("type")=="text")
print(f"Text: {text}")
s, e = text.find("{"), text.rfind("}")+1
url_map = json.loads(text[s:e]) if s>=0 and e>s else {}
print(f"URL map: {url_map}")
print("=== TESTING DB ===")
conn = psycopg2.connect(DB_URL)
cur = conn.cursor()
cur.execute("SELECT id, name, website FROM eu_alternatives WHERE LOWER(name) = LOWER(%s)", ("Plausible",))
print(f"Plausible row: {cur.fetchall()}")
cur.execute("UPDATE eu_alternatives SET website = %s WHERE LOWER(name) = LOWER(%s)", ("https://plausible.io", "Plausible"))
print(f"Update rowcount: {cur.rowcount}")
conn.commit()
cur.close()
conn.close()
