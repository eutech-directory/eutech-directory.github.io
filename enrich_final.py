import time, json, requests, psycopg2, os, subprocess

DB_URL = "postgresql://agentuser:agentstack123@localhost:5432/agentstack"
API_URL = "https://api.anthropic.com/v1/messages"
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
MODEL = "claude-sonnet-4-6"
BATCH_SIZE = 10
DELAY = 2

def get_tools():
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    cur.execute("SELECT id, name, category FROM eu_alternatives WHERE (website IS NULL OR website = '') AND name IS NOT NULL ORDER BY id")
    tools = cur.fetchall()
    cur.close()
    conn.close()
    print(f"Found {len(tools)} tools missing URLs")
    return tools

def lookup(batch):
    lines = "\n".join([f"- {t[1]} ({t[2]})" for t in batch])
    prompt = "Return ONLY a valid JSON object mapping each tool name to its official website URL. If unknown use null. No explanation, no markdown.\n" + lines
    try:
        r = requests.post(
            API_URL,
            headers={"Content-Type": "application/json", "x-api-key": API_KEY, "anthropic-version": "2023-06-01"},
            json={"model": MODEL, "max_tokens": 1000, "messages": [{"role": "user", "content": prompt}]},
            timeout=60
        )
        data = r.json()
        text = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
        s, e = text.find("{"), text.rfind("}") + 1
        if s >= 0 and e > s:
            return json.loads(text[s:e])
    except Exception as ex:
        print(f"  API error: {ex}")
    return {}

def update(url_map):
    if not url_map:
        return 0
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    n = 0
    for name, url in url_map.items():
        if not url:
            continue
        if not url.startswith("http"):
            url = "https://" + url
        try:
            cur.execute(
                "UPDATE eu_alternatives SET website = %s WHERE (website IS NULL OR website = '') AND LOWER(name) = LOWER(%s)",
                (url, name)
            )
            n += cur.rowcount
        except Exception:
            conn.rollback()
    conn.commit()
    cur.close()
    conn.close()
    return n

tools = get_tools()
batches = [tools[i:i+BATCH_SIZE] for i in range(0, len(tools), BATCH_SIZE)]
print(f"Processing {len(batches)} batches...")
total = 0
for i, batch in enumerate(batches):
    print(f"Batch {i+1}/{len(batches)}: {[t[1] for t in batch]}")
    try:
        url_map = lookup(batch)
        n = update(url_map)
        total += n
        print(f"  Updated {n}")
    except Exception as ex:
        print(f"  Error: {ex}")
    time.sleep(DELAY)

print(f"\nDone. Total updated: {total}")

conn = psycopg2.connect(DB_URL)
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM eu_alternatives WHERE website IS NOT NULL AND website != ''")
with_url = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM eu_alternatives")
total_tools = cur.fetchone()[0]
cur.close()
conn.close()
print(f"Tools with URLs: {with_url}/{total_tools}")

print("\nRegenerating index.html and pushing to GitHub...")
os.chdir(r"C:\Users\USER\NANO\outputs\eutech-directory")
os.system(r"C:\ProgramData\miniconda3\envs\agentstack\python.exe C:\Users\USER\.nanobot\skills\products\generate_directory.py")
os.system('git add index.html && git commit -m "Enrich: all tool URLs updated" && git push origin main')
print("All done! https://eutech-directory.github.io")

