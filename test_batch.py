import requests, json, os, psycopg2

DB_URL = "postgresql://agentuser:agentstack123@localhost:5432/agentstack"
API_URL = "https://api.anthropic.com/v1/messages"
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
MODEL = "claude-sonnet-4-6"

conn = psycopg2.connect(DB_URL)
cur = conn.cursor()
cur.execute("SELECT id, name, category FROM eu_alternatives WHERE (website IS NULL OR website = '') AND name IS NOT NULL ORDER BY id LIMIT 5")
tools = cur.fetchall()
cur.close()
conn.close()
print(f"Tools: {[t[1] for t in tools]}")

lines = "\n".join([f"- {t[1]} ({t[2]})" for t in tools])
prompt = "Return ONLY a valid JSON object mapping each tool name to its official website URL. If unknown use null. No explanation, no markdown.\n" + lines

r = requests.post(
    API_URL,
    headers={"Content-Type": "application/json", "x-api-key": API_KEY},
    json={"model": MODEL, "max_tokens": 1000, "messages": [{"role": "user", "content": prompt}]},
    timeout=60
)

print(f"Status: {r.status_code}")
data = r.json()
print(f"Content blocks: {data.get('content', [])}")
text = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
print(f"Text: '{text}'")
s, e = text.find("{"), text.rfind("}") + 1
if s >= 0 and e > s:
    try:
        parsed = json.loads(text[s:e])
        print(f"Parsed OK: {parsed}")
        # Try DB update
        conn2 = psycopg2.connect(DB_URL)
        cur2 = conn2.cursor()
        for name, url in parsed.items():
            if url:
                cur2.execute("UPDATE eu_alternatives SET website = %s WHERE (website IS NULL OR website = '') AND LOWER(name) = LOWER(%s)", (url, name))
                print(f"  {name} -> {url} (rows: {cur2.rowcount})")
        conn2.commit()
        cur2.close()
        conn2.close()
    except Exception as ex:
        print(f"Error: {ex}")
        print(f"Raw: '{text[s:e]}'")
else:
    print(f"No JSON. Full response: {json.dumps(data)[:500]}")
