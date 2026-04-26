"""
build_eutech_index.py
====================
Generates a complete clean index.html for eutech.directory from the DB.
Run this instead of patching files — avoids all encoding corruption.

    python build_eutech_index.py
"""

import json
import re
import subprocess
from datetime import datetime
from pathlib import Path

import psycopg2
import psycopg2.extras

DB_URL    = "postgresql://agentuser:agentstack123@localhost:5432/agentstack"
OUT_FILE  = Path(r"C:\Users\USER\NANO\outputs\eutech-directory\index.html")
GIT_DIR   = Path(r"C:\Users\USER\NANO\outputs\eutech-directory")


def get_tools():
    conn = psycopg2.connect(DB_URL)
    cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT name, category, description, country, website, verified
        FROM eu_alternatives
        WHERE verified = TRUE
        ORDER BY category, name
    """)
    tools = cur.fetchall()
    conn.close()
    return tools


def build_tools_json(tools):
    tools_list = []
    for t in tools:
        # Strip all non-ASCII characters from description at build time
        # Prevents any DB encoding issues from reaching the published site
        desc = (t["description"] or "")[:200]
        desc = desc.encode("ascii", errors="ignore").decode("ascii").strip()
        tools_list.append({
            "n":  (t["name"] or ""),
            "c":  (t["category"] or "Other"),
            "d":  desc,
            "co": (t["country"] or ""),
            "fl": "UK" if t["country"] == "GB" else "",
            "w":  (t["website"] or ""),
            "v":  True,
        })
    return json.dumps(tools_list, ensure_ascii=True, separators=(",", ":"))


def get_cat_counts(tools):
    from collections import Counter
    counts = Counter(t["category"] or "Other" for t in tools)
    return dict(counts)


def build_cat_buttons(counts):
    cats = [
        "Other", "Analytics & Data", "Email & Communication",
        "Cloud & Hosting", "Project Management", "AI & Automation",
        "Security & Privacy", "Developer Tools", "Storage & Backup",
        "HR & Team", "Finance & Payments", "Marketing & SEO"
    ]
    buttons = []
    for cat in cats:
        count = counts.get(cat, 0)
        if count > 0:
            safe = cat.replace("&", "&amp;")
            buttons.append(
                f'<button class="cat-btn" data-cat="{cat}" '
                f'onclick="filterCat(this)">{safe} '
                f'<span class="cat-count">{count}</span></button>'
            )
    return "\n  ".join(buttons)


def build_html(tools, tools_json, cat_buttons, total_in_db):
    verified = len(tools)
    uk_count = sum(1 for t in tools if t["country"] == "GB")
    today    = datetime.now().strftime("%B %Y")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <meta name="description" content="The definitive directory of EU-built software alternatives. {verified} verified European and UK tools across every category. GDPR by default, no US cloud."/>
  <title>eutech.directory &mdash; European software alternatives</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    :root {{
      --bg:        #0d1117;
      --surface:   #161b22;
      --border:    #21262d;
      --accent:    #2563eb;
      --accent-h:  #1d4ed8;
      --text:      #e6edf3;
      --muted:     #8b949e;
      --tag-bg:    #1f2937;
      --verified:  #16a34a;
      --radius:    10px;
      --card-w:    320px;
    }}

    html {{ scroll-behavior: smooth; }}

    body {{
      background: var(--bg);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      font-size: 15px;
      line-height: 1.6;
      min-height: 100vh;
    }}

    /* Header */
    header {{
      background: linear-gradient(160deg, #0f172a 0%, #1e3a5f 100%);
      border-bottom: 1px solid var(--border);
      padding: 60px 24px 48px;
      text-align: center;
    }}
    .logo {{ font-size: 2.6rem; font-weight: 800; letter-spacing: -0.5px; color: #fff; }}
    .logo span {{ color: var(--accent); }}
    .tagline {{ margin-top: 10px; font-size: 1.05rem; color: #94a3b8; max-width: 520px; margin-left: auto; margin-right: auto; }}
    .stats {{ margin-top: 28px; display: flex; justify-content: center; gap: 32px; flex-wrap: wrap; }}
    .stat {{ text-align: center; }}
    .stat-num {{ font-size: 1.9rem; font-weight: 700; color: #fff; }}
    .stat-label {{ font-size: 0.78rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.08em; margin-top: 2px; }}

    /* Search */
    .search-wrap {{ max-width: 600px; margin: 32px auto 0; padding: 0 24px; position: relative; }}
    #search {{
      width: 100%; padding: 12px 16px; background: var(--surface);
      border: 1px solid var(--border); border-radius: var(--radius);
      color: var(--text); font-size: 1rem; outline: none;
    }}
    #search:focus {{ border-color: var(--accent); }}
    #search::placeholder {{ color: var(--muted); }}
    .ac-dropdown {{
      position: absolute; top: 100%; left: 24px; right: 24px;
      background: var(--surface); border: 1px solid var(--border);
      border-radius: var(--radius); z-index: 100; display: none; max-height: 260px; overflow-y: auto;
    }}
    .ac-item {{ padding: 10px 16px; cursor: pointer; font-size: 0.9rem; }}
    .ac-item:hover, .ac-item.focused {{ background: var(--tag-bg); }}

    /* Category bar */
    .cat-bar {{ display: flex; flex-wrap: wrap; gap: 8px; padding: 24px 24px 0; max-width: 1200px; margin: 0 auto; }}
    .cat-btn, .all-btn {{
      padding: 6px 14px; border-radius: 20px; border: 1px solid var(--border);
      background: var(--surface); color: var(--muted); font-size: 0.82rem;
      cursor: pointer; transition: all 0.15s; white-space: nowrap;
    }}
    .cat-btn:hover, .all-btn:hover {{ border-color: var(--accent); color: var(--text); }}
    .cat-btn.active, .all-btn.active {{ background: var(--accent); border-color: var(--accent); color: #fff; }}
    .cat-count {{ opacity: 0.7; font-size: 0.75rem; }}

    /* Results bar */
    .results-bar {{ display: flex; align-items: center; justify-content: space-between; padding: 16px 24px; max-width: 1200px; margin: 0 auto; }}
    #result-count {{ color: var(--muted); font-size: 0.85rem; }}
    .clear-btn {{ background: none; border: none; color: var(--accent); cursor: pointer; font-size: 0.85rem; }}

    /* Grid */
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(var(--card-w), 1fr));
      gap: 16px; padding: 0 24px 48px; max-width: 1200px; margin: 0 auto;
    }}

    /* Card */
    .card {{
      background: var(--surface); border: 1px solid var(--border);
      border-radius: var(--radius); padding: 18px 20px;
      display: flex; flex-direction: column; gap: 10px;
      transition: border-color 0.15s, transform 0.1s;
    }}
    .card:hover {{ border-color: var(--accent); transform: translateY(-2px); }}
    .card-top {{ display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; }}
    .card-name {{ font-weight: 600; font-size: 0.95rem; display: flex; align-items: center; gap: 6px; }}
    .verified-dot {{ width: 7px; height: 7px; border-radius: 50%; background: var(--verified); display: inline-block; flex-shrink: 0; }}
    .uk-badge {{ font-size: 0.65rem; background: #1e3a5f; color: #60a5fa; border-radius: 4px; padding: 1px 5px; font-weight: 600; }}
    .card-cat {{ font-size: 0.72rem; background: var(--tag-bg); color: var(--muted); padding: 3px 8px; border-radius: 4px; white-space: nowrap; }}
    .card-desc {{ font-size: 0.83rem; color: var(--muted); line-height: 1.5; flex: 1; }}
    .card-link {{ font-size: 0.8rem; color: var(--accent); text-decoration: none; word-break: break-all; }}
    .card-link:hover {{ text-decoration: underline; }}

    /* Empty state */
    #empty {{ display: none; text-align: center; padding: 60px 24px; color: var(--muted); }}
    #empty p {{ font-size: 1rem; margin-top: 8px; }}

    /* Listing criteria */
    .listing-criteria {{
      background: var(--surface); border-top: 1px solid var(--border);
      padding: 48px 24px; max-width: 800px; margin: 0 auto; text-align: center;
    }}
    .listing-criteria h2 {{ font-size: 1.5rem; font-weight: 700; margin-bottom: 10px; }}
    .criteria-intro {{ color: var(--muted); font-size: 0.95rem; margin-bottom: 28px; max-width: 540px; margin-left: auto; margin-right: auto; }}
    .criteria-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 24px; text-align: left; }}
    @media (max-width: 600px) {{ .criteria-grid {{ grid-template-columns: 1fr; }} }}
    .criterion {{ display: flex; gap: 12px; align-items: flex-start; background: var(--bg); border: 1px solid var(--border); border-radius: var(--radius); padding: 14px 16px; }}
    .criterion-icon {{ font-size: 1.4rem; flex-shrink: 0; margin-top: 2px; }}
    .criterion strong {{ display: block; font-size: 0.9rem; margin-bottom: 3px; }}
    .criterion p {{ font-size: 0.82rem; color: var(--muted); line-height: 1.4; margin: 0; }}
    .criteria-cta {{ font-size: 0.9rem; color: var(--accent); font-weight: 500; }}

    /* Submit section */
    .submit-section {{
      background: var(--surface); border-top: 1px solid var(--border);
      padding: 48px 24px; text-align: center;
    }}
    .submit-section h2 {{ font-size: 1.4rem; font-weight: 700; margin-bottom: 8px; }}
    .submit-section p {{ color: var(--muted); font-size: 0.9rem; margin-bottom: 28px; }}
    #submit-form {{ max-width: 520px; margin: 0 auto; display: flex; flex-direction: column; gap: 12px; }}
    #submit-form input, #submit-form textarea, #submit-form select {{
      width: 100%; padding: 12px 16px; background: var(--bg);
      border: 1px solid var(--border); border-radius: var(--radius);
      color: var(--text); font-size: 0.9rem; outline: none; transition: border-color 0.15s;
    }}
    #submit-form input:focus, #submit-form textarea:focus, #submit-form select:focus {{ border-color: var(--accent); }}
    #submit-form textarea {{ resize: vertical; min-height: 80px; }}
    #submit-form select option {{ background: var(--surface); }}
    .submit-btn {{
      padding: 13px; background: var(--accent); color: #fff;
      border: none; border-radius: var(--radius); font-size: 0.95rem;
      font-weight: 600; cursor: pointer; transition: background 0.15s;
    }}
    .submit-btn:hover {{ background: var(--accent-h); }}
    #form-success {{ display: none; color: var(--verified); padding: 12px; font-size: 0.9rem; }}

    /* Footer */
    footer {{ text-align: center; padding: 24px; color: #64748b; font-size: 0.8rem; border-top: 1px solid var(--border); }}

    @media (max-width: 600px) {{
      .logo {{ font-size: 2rem; }}
      .stat-num {{ font-size: 1.4rem; }}
      .grid {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>

<header>
  <div class="logo">eutech<span>.</span>directory</div>
  <p class="tagline">The definitive directory of EU-built software. No US cloud dependencies, GDPR by default.</p>
  <div class="stats">
    <div class="stat">
      <div class="stat-num" id="total-count">{verified}</div>
      <div class="stat-label">Verified live</div>
    </div>
    <div class="stat">
      <div class="stat-num">12</div>
      <div class="stat-label">categories</div>
    </div>
    <div class="stat">
      <div class="stat-num">{total_in_db}</div>
      <div class="stat-label">total tools</div>
    </div>
  </div>
  <div class="search-wrap">
    <input type="text" id="search" placeholder="Search tools..." oninput="onSearch(this.value)" onkeydown="acKey(event)" autocomplete="off"/>
    <div class="ac-dropdown" id="ac"></div>
  </div>
</header>

<div class="cat-bar">
  <button class="all-btn active" onclick="filterCat(this)" data-cat="">All categories</button>
  {cat_buttons}
</div>

<div class="results-bar">
  <span id="result-count">{verified} tools</span>
  <button class="clear-btn" onclick="clearFilters()">Clear filters</button>
</div>

<div id="grid" class="grid"></div>
<div id="empty"><p>No tools found matching your search.</p></div>

<div class="listing-criteria">
  <h2>How to get listed</h2>
  <p class="criteria-intro">eutech.directory lists EU-built and EU-hosted software. To be included, your tool must meet all criteria:</p>
  <div class="criteria-grid">
    <div class="criterion">
      <span class="criterion-icon">&#127466;&#127482;</span>
      <div>
        <strong>EU-built or EU-hosted</strong>
        <p>Company founded in the EU, or primary servers in EU data centres.</p>
      </div>
    </div>
    <div class="criterion">
      <span class="criterion-icon">&#128274;</span>
      <div>
        <strong>GDPR compliant by default</strong>
        <p>Data protection built into the architecture &mdash; not just a checkbox.</p>
      </div>
    </div>
    <div class="criterion">
      <span class="criterion-icon">&#9729;&#65039;</span>
      <div>
        <strong>No US cloud dependencies</strong>
        <p>Data does not transit through or rest on AWS, GCP, or Azure US regions.</p>
      </div>
    </div>
    <div class="criterion">
      <span class="criterion-icon">&#9989;</span>
      <div>
        <strong>Actively maintained</strong>
        <p>Live, usable, and updated within the last 12 months.</p>
      </div>
    </div>
  </div>
  <p class="criteria-cta">Meet all criteria? Submit below &mdash; we review within 24 hours.</p>
</div>

<div class="submit-section">
  <h2>Submit your tool</h2>
  <p>Know an EU-built alternative we&apos;re missing? Add it to the directory.</p>
  <form id="submit-form" action="https://formspree.io/f/xqewnpwl" method="POST">
    <input type="text" name="tool_name" placeholder="Tool name" required/>
    <input type="url" name="website" placeholder="Website URL (https://...)" required/>
    <select name="category">
      <option value="" disabled selected>Select category</option>
      <option>Cloud &amp; Hosting</option>
      <option>Email &amp; Communication</option>
      <option>Project Management</option>
      <option>Analytics &amp; Data</option>
      <option>Security &amp; Privacy</option>
      <option>Storage &amp; Backup</option>
      <option>Developer Tools</option>
      <option>Finance &amp; Payments</option>
      <option>HR &amp; Team</option>
      <option>Marketing &amp; SEO</option>
      <option>AI &amp; Automation</option>
      <option>Other</option>
    </select>
    <input type="text" name="replaces" placeholder="Replaces which US tool? (e.g. Slack, Dropbox)"/>
    <textarea name="description" placeholder="Short description (1-2 sentences)"></textarea>
    <button type="submit" class="submit-btn">Submit tool &rarr;</button>
    <div id="form-success">Thanks! We&apos;ll review and add it within 24 hours.</div>
  </form>
</div>

<footer>
  eutech.directory &mdash; {today} &mdash; {total_in_db} EU+UK tools indexed
</footer>

<script>
const TOOLS = {tools_json};

let activeCategory = "";
let acIndex = -1;

function renderCards(tools) {{
  const grid = document.getElementById("grid");
  const empty = document.getElementById("empty");
  if (!tools.length) {{ grid.innerHTML = ""; empty.style.display = "block"; return; }}
  empty.style.display = "none";
  grid.innerHTML = tools.map(t => {{
    const dot  = t.v ? '<span class="verified-dot" title="Verified live"></span>' : "";
    const link = t.w ? '<a class="card-link" href="' + t.w + '" target="_blank" rel="noopener noreferrer">' + t.w.replace(/^https?:\\/\\/(www\\.)?/, "") + '</a>' : "";
    const uk   = t.fl ? '<span class="uk-badge">' + t.fl + '</span>' : "";
    return '<div class="card"><div class="card-top"><div class="card-name">' + t.n + uk + dot + '</div><span class="card-cat">' + t.c + '</span></div><p class="card-desc">' + (t.d || t.n) + '</p>' + link + '</div>';
  }}).join("");
  document.getElementById("result-count").textContent = tools.length + " tools";
}}

function getFiltered() {{
  let f = TOOLS;
  if (activeCategory) f = f.filter(t => t.c === activeCategory);
  const q = (document.getElementById("search").value || "").toLowerCase();
  if (q) f = f.filter(t => t.n.toLowerCase().includes(q) || (t.d||"").toLowerCase().includes(q));
  return f;
}}

function applyFilters() {{ renderCards(getFiltered()); }}

function filterCat(btn) {{
  const cat = btn.dataset.cat;
  activeCategory = (activeCategory === cat && cat !== "") ? "" : cat;
  document.querySelectorAll(".cat-btn, .all-btn").forEach(b => b.classList.remove("active"));
  if (!activeCategory) document.querySelector(".all-btn").classList.add("active");
  else btn.classList.add("active");
  acClose();
  applyFilters();
}}

function clearFilters() {{
  activeCategory = "";
  document.getElementById("search").value = "";
  document.querySelectorAll(".cat-btn, .all-btn").forEach(b => b.classList.remove("active"));
  document.querySelector(".all-btn").classList.add("active");
  acClose();
  applyFilters();
}}

function onSearch(val) {{
  applyFilters();
  const q = val.toLowerCase();
  const ac = document.getElementById("ac");
  if (!q || q.length < 2) {{ acClose(); return; }}
  const matches = TOOLS.filter(t => t.n.toLowerCase().startsWith(q)).slice(0, 8);
  if (!matches.length) {{ acClose(); return; }}
  ac.innerHTML = matches.map((t, i) => '<div class="ac-item" data-idx="' + i + '" onclick="acSelect(this.dataset.name)"  data-name="' + t.n.replace(/"/g, '&quot;') + '">' + t.n + ' <span style="color:var(--muted);font-size:0.75rem">' + t.c + '</span></div>').join("");
  ac.style.display = "block";
  acIndex = -1;
}}

function acSelect(name) {{
  document.getElementById("search").value = name;
  acClose();
  applyFilters();
}}

function acClose() {{
  document.getElementById("ac").style.display = "none";
  acIndex = -1;
}}

function acKey(e) {{
  const items = document.querySelectorAll(".ac-item");
  if (e.key === "ArrowDown") {{ acIndex = Math.min(acIndex + 1, items.length - 1); acFocus(items); }}
  else if (e.key === "ArrowUp") {{ acIndex = Math.max(acIndex - 1, 0); acFocus(items); }}
  else if (e.key === "Enter" && acIndex >= 0) {{ items[acIndex].click(); e.preventDefault(); }}
  else if (e.key === "Escape") {{ acClose(); }}
}}

function acFocus(items) {{
  items.forEach((el, i) => el.classList.toggle("focused", i === acIndex));
  if (items[acIndex]) items[acIndex].scrollIntoView({{ block: "nearest" }});
}}

document.addEventListener("click", e => {{
  if (!e.target.closest(".search-wrap")) acClose();
}});

document.getElementById("submit-form").addEventListener("submit", async function(e) {{
  e.preventDefault();
  const btn = this.querySelector(".submit-btn");
  btn.textContent = "Submitting...";
  btn.disabled = true;
  try {{
    const res = await fetch(this.action, {{
      method: "POST", body: new FormData(this), headers: {{ Accept: "application/json" }},
    }});
    if (res.ok) {{
      this.reset();
      document.getElementById("form-success").style.display = "block";
      btn.textContent = "Submit tool";
      btn.disabled = false;
    }} else {{
      btn.textContent = "Error - try again";
      btn.disabled = false;
    }}
  }} catch (_) {{
    btn.textContent = "Error - try again";
    btn.disabled = false;
  }}
}});

document.querySelector(".all-btn").classList.add("active");
renderCards(TOOLS);
</script>

</body>
</html>"""


def main():
    print("Loading tools from DB...")
    tools = get_tools()
    print(f"  {len(tools)} verified tools")

    # Get total count including unverified
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM eu_alternatives")
    total_in_db = cur.fetchone()[0]
    conn.close()

    tools_json  = build_tools_json(tools)
    cat_counts  = get_cat_counts(tools)
    cat_buttons = build_cat_buttons(cat_counts)
    html        = build_html(tools, tools_json, cat_buttons, total_in_db)

    OUT_FILE.write_text(html, encoding="utf-8")
    print(f"  Written: {OUT_FILE}")

    # Verify clean
    import re
    garbled = re.findall(r'[ÃÂ][ÃÂ\x80-\xff]+', html)
    print(f"  Clean: {len(garbled)} encoding issues" if garbled else "  Clean: no encoding issues")

    # Git push
    try:
        subprocess.run(["git", "-C", str(GIT_DIR), "add", "index.html"],
                       check=True, capture_output=True)
        result = subprocess.run(
            ["git", "-C", str(GIT_DIR), "commit", "-m",
             f"Rebuild index.html: {len(tools)} verified tools — {datetime.now().strftime('%Y-%m-%d')}"],
            capture_output=True, text=True
        )
        if "nothing to commit" in result.stdout:
            print("  No changes to push")
        else:
            subprocess.run(["git", "-C", str(GIT_DIR), "push"],
                           check=True, capture_output=True)
            print("  Pushed to GitHub Pages")
    except Exception as e:
        print(f"  Git error: {e}")

    print(f"\nDone. {len(tools)} tools live at eutech-directory.github.io")


if __name__ == "__main__":
    main()
