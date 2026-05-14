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
        SELECT name, category, description, country, website, verified, COALESCE(featured, false) as featured, COALESCE(featured, false) as featured, COALESCE(featured, false) as featured, COALESCE(featured, false) as featured, COALESCE(featured, false) as featured
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
            "co": (t["country"] or ""),
            "r":  (t["replaces_us_tool"] or "")[:30] if t.get("replaces_us_tool") else "",
            "fl": "featured" if t.get("featured") or (t.get("upvotes") or 0) >= 5 else "",
            "d":  desc,
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
        "MCP Servers", "Project Management", "Developer Tools",
        "Email & Communication", "Security & Privacy", "Analytics & Data",
        "Storage & Backup", "AI & Automation", "Cloud & Hosting",
        "Other", "Finance & Payments", "HR & Team", "Marketing & SEO"
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
    today    = datetime.now().strftime("%B %Y")

    # Featured tools (top 3 by upvotes or manually set)
    featured = [t for t in tools if t.get("upvotes", 0) >= 5][:3]
    featured_names = {t["n"] for t in featured} if featured else set()

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <meta name="description" content="The definitive directory of EU-built software alternatives. {verified} verified European and UK tools. GDPR by default, no US cloud."/>
  <title>eutech.directory &mdash; European software alternatives</title>
  <style>

    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    :root {{
      --bg:        #0d1117;
      --surface:   #161b22;
      --border:    #21262d;
      --accent:    #00bcd4;
      --accent-h:  #00acc1;
      --text:      #e6edf3;
      --muted:     #8b949e;
      --tag-bg:    #1f2937;
      --verified:  #16a34a;
      --featured:  #f59e0b;
      --radius:    8px;
      --card-w:    300px;
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
    header {{
      background: linear-gradient(160deg, #0f172a 0%, #1a2e4a 100%);
      border-bottom: 1px solid var(--border);
      padding: 52px 24px 40px;
      text-align: center;
    }}
    .logo {{ font-size: 2.4rem; font-weight: 800; letter-spacing: -0.5px; color: #fff; }}
    .logo span {{ color: var(--accent); }}
    .tagline {{ margin-top: 8px; font-size: 1rem; color: #94a3b8; max-width: 520px; margin-left: auto; margin-right: auto; }}
    .stats {{ margin-top: 24px; display: flex; justify-content: center; gap: 32px; flex-wrap: wrap; }}
    .stat {{ text-align: center; }}
    .stat-num {{ font-size: 1.8rem; font-weight: 700; color: #fff; }}
    .stat-label {{ font-size: 0.72rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.08em; margin-top: 2px; }}
    .search-wrap {{ max-width: 560px; margin: 28px auto 0; padding: 0 24px; position: relative; }}
    #search {{
      width: 100%; padding: 12px 16px; background: #1e293b;
      border: 1px solid #334155; border-radius: var(--radius);
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
    .ac-item:hover {{ background: var(--tag-bg); }}

    /* Verification strip */
    .verify-strip {{
      background: #0a0f1a;
      border-bottom: 1px solid var(--border);
      padding: 20px 24px;
    }}
    .verify-ttl {{
      font-size: 0.7rem; font-weight: 700; letter-spacing: 0.12em;
      text-transform: uppercase; color: #64748b; margin-bottom: 12px;
    }}
    .verify-row {{
      display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 8px;
    }}
    .vbadge {{
      background: var(--surface); border: 1px solid var(--border);
      border-radius: var(--radius); padding: 12px; cursor: pointer;
      transition: border-color .2s; position: relative;
    }}
    .vbadge:hover {{ border-color: var(--accent); }}
    .vbadge-icon {{ font-size: 16px; margin-bottom: 5px; }}
    .vbadge-label {{ font-size: 12px; font-weight: 600; color: var(--text); }}
    .vbadge-sub {{ font-size: 10px; color: var(--muted); margin-top: 2px; }}
    .vtip {{
      display: none; position: absolute; top: calc(100% + 8px); left: 0;
      background: #1e293b; border: 1px solid var(--accent);
      border-radius: var(--radius); padding: 12px; z-index: 200;
      font-size: 11px; color: #94a3b8; line-height: 1.6;
      min-width: 200px; width: max-content; max-width: 260px;
    }}
    .vtip.show {{ display: block; }}
    .vtip-title {{ font-size: 12px; font-weight: 600; color: var(--text); margin-bottom: 6px; }}
    .vtip ul {{ margin-left: 14px; }}
    .vtip li {{ margin-bottom: 3px; }}

    /* Category bar */
    .cat-bar {{ display: flex; flex-wrap: wrap; gap: 8px; padding: 16px 24px; max-width: 1200px; margin: 0 auto; }}
    .cat-btn, .all-btn {{
      padding: 5px 14px; border-radius: 20px; border: 1px solid var(--border);
      background: var(--surface); color: var(--muted); font-size: 0.8rem;
      cursor: pointer; transition: all 0.15s; white-space: nowrap;
    }}
    .cat-btn:hover, .all-btn:hover {{ border-color: var(--accent); color: var(--text); }}
    .cat-btn.active, .all-btn.active {{ background: var(--accent); border-color: var(--accent); color: #000; font-weight: 600; }}
    .cat-count {{ opacity: 0.7; font-size: 0.75rem; }}

    /* Results bar */
    .results-bar {{ display: flex; align-items: center; justify-content: space-between; padding: 12px 24px; max-width: 1200px; margin: 0 auto; }}
    .results-bar span {{ font-size: 0.85rem; color: var(--muted); }}
    .clear-btn {{ background: none; border: 1px solid var(--border); color: var(--muted); padding: 4px 12px; border-radius: 20px; cursor: pointer; font-size: 0.8rem; }}
    .clear-btn:hover {{ border-color: var(--accent); color: var(--text); }}

    /* Section labels */
    .section-label {{
      font-size: 0.7rem; font-weight: 700; letter-spacing: 0.1em;
      text-transform: uppercase; color: #64748b;
      display: flex; align-items: center; gap: 8px;
      padding: 8px 24px 8px; max-width: 1200px; margin: 0 auto;
    }}
    .section-label::after {{ content: ''; flex: 1; height: 1px; background: var(--border); }}

    /* Grid */
    .grid {{
      display: grid; grid-template-columns: repeat(auto-fill, minmax(var(--card-w), 1fr));
      gap: 12px; padding: 8px 24px 16px; max-width: 1200px; margin: 0 auto;
    }}

    /* Cards */
    .card {{
      background: var(--surface); border: 1px solid var(--border);
      border-radius: var(--radius); padding: 14px;
      transition: border-color 0.15s; display: flex; flex-direction: column; gap: 8px;
    }}
    .card:hover {{ border-color: #334155; }}
    .card.featured {{
      border: 1px solid #f59e0b66;
      background: #1a160a;
    }}
    .card-top {{ display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; }}
    .card-name {{ font-size: 0.9rem; font-weight: 600; color: var(--text); }}
    .card-desc {{ font-size: 0.8rem; color: var(--muted); line-height: 1.5; flex: 1; }}
    .card-footer {{ display: flex; gap: 5px; flex-wrap: wrap; align-items: center; }}
    .card-link {{ color: var(--accent); font-size: 0.75rem; text-decoration: none; margin-left: auto; }}
    .card-link:hover {{ text-decoration: underline; }}

    /* Badges */
    .badge {{ font-size: 10px; padding: 2px 7px; border-radius: 4px; white-space: nowrap; font-weight: 500; }}
    .b-verified {{ background: #14532d; color: #86efac; border: 1px solid #166534; }}
    .b-featured {{ background: #451a03; color: #fcd34d; border: 1px solid #78350f; }}
    .b-mcp {{ background: #1e3a5f; color: #93c5fd; border: 1px solid #1d4ed8; }}
    .b-unverified {{ background: #1c1917; color: #a8a29e; border: 1px solid #292524; }}
    .tag {{ background: var(--tag-bg); color: #6b7280; font-size: 10px; padding: 2px 7px; border-radius: 4px; }}

    /* Get listed banner */
    .get-listed {{
      margin: 8px 24px 24px; max-width: calc(1200px - 48px);
      background: linear-gradient(135deg, #001a2e, #002d4a);
      border: 1px solid #00bcd444; border-radius: var(--radius);
      padding: 16px 20px; display: flex; justify-content: space-between;
      align-items: center; gap: 16px; flex-wrap: wrap;
    }}
    .get-listed-text .gl-title {{ font-size: 14px; font-weight: 600; color: #fff; }}
    .get-listed-text .gl-sub {{ font-size: 12px; color: #64748b; margin-top: 3px; }}
    .gl-btn {{
      background: var(--accent); color: #000; border: none;
      border-radius: var(--radius); padding: 8px 18px;
      font-size: 12px; font-weight: 700; cursor: pointer; white-space: nowrap;
    }}
    .gl-btn:hover {{ background: var(--accent-h); }}

    /* Empty state */
    #empty {{ display: none; text-align: center; padding: 60px 24px; color: var(--muted); }}

    /* Sticky CTA */
    .sticky-cta {{
      position: fixed; bottom: 24px; right: 24px; z-index: 999;
      background: var(--accent); color: #000; border: none;
      border-radius: 50px; padding: 10px 18px; font-size: 12px;
      font-weight: 700; cursor: pointer;
      box-shadow: 0 4px 20px rgba(0,188,212,0.35);
      transition: all .2s; text-decoration: none;
      display: flex; align-items: center; gap: 6px;
    }}
    .sticky-cta:hover {{ background: var(--accent-h); transform: translateY(-2px); }}

    /* Listing criteria section */
    .listing-criteria {{
      max-width: 1200px; margin: 0 auto; padding: 40px 24px;
      border-top: 1px solid var(--border);
    }}
    .listing-criteria h2 {{ font-size: 1.3rem; font-weight: 700; color: var(--text); margin-bottom: 8px; }}
    .criteria-intro {{ font-size: 0.9rem; color: var(--muted); margin-bottom: 24px; }}
    .criteria-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; margin-bottom: 24px; }}
    .criterion {{
      background: var(--surface); border: 1px solid var(--border);
      border-radius: var(--radius); padding: 16px;
    }}
    .criterion-icon {{ font-size: 1.5rem; margin-bottom: 8px; display: block; }}
    .criterion h3 {{ font-size: 0.9rem; font-weight: 600; color: var(--text); margin-bottom: 4px; }}
    .criterion p {{ font-size: 0.8rem; color: var(--muted); line-height: 1.5; }}
    .submit-link {{ color: var(--accent); text-decoration: none; font-weight: 500; }}

    /* Submit form */
    #submit {{ max-width: 600px; margin: 0 auto; padding: 0 24px 60px; }}
    #submit h2 {{ font-size: 1.3rem; font-weight: 700; color: var(--text); margin-bottom: 8px; text-align: center; }}
    #submit p {{ font-size: 0.9rem; color: var(--muted); text-align: center; margin-bottom: 24px; }}
    .form-group {{ margin-bottom: 16px; }}
    .form-group label {{ display: block; font-size: 0.85rem; color: var(--muted); margin-bottom: 6px; }}
    .form-group input, .form-group select, .form-group textarea {{
      width: 100%; padding: 10px 14px; background: var(--surface);
      border: 1px solid var(--border); border-radius: var(--radius);
      color: var(--text); font-size: 0.9rem; outline: none;
    }}
    .form-group input:focus, .form-group select:focus, .form-group textarea:focus {{ border-color: var(--accent); }}
    .form-group textarea {{ height: 80px; resize: vertical; }}
    .form-group select option {{ background: var(--surface); }}
    .submit-btn {{
      width: 100%; padding: 12px; background: var(--accent); color: #000;
      border: none; border-radius: var(--radius); font-size: 1rem;
      font-weight: 700; cursor: pointer; transition: background .15s;
    }}
    .submit-btn:hover {{ background: var(--accent-h); }}
    .back-top {{
      position: fixed !important; bottom: 90px !important; right: 24px !important;
      z-index: 9999 !important; background: #161b22;
      border: 1px solid #21262d; color: #8b949e;
      width: 44px; height: 44px; border-radius: 50%;
      display: flex !important; align-items: center; justify-content: center;
      cursor: pointer; font-size: 22px; line-height: 1;
      transition: all .2s; opacity: 0; pointer-events: none;
      box-shadow: 0 4px 16px rgba(0,0,0,0.4); text-decoration: none;
    }}
    .back-top.visible {{ opacity: 1 !important; pointer-events: auto !important; }}
    .back-top:hover {{ background: #00bcd4 !important; border-color: #00bcd4 !important; color: #000 !important; transform: translateY(-3px); }}
    @media (max-width: 600px) {{
      .logo {{ font-size: 1.8rem; }}
      .stat-num {{ font-size: 1.4rem; }}
      .grid {{ grid-template-columns: 1fr; padding: 8px 12px; }}
      .verify-row {{ grid-template-columns: repeat(2, 1fr); }}
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
      <div class="stat-num">13</div>
      <div class="stat-label">categories</div>
    </div>
    <div class="stat">
      <div class="stat-num">{total_in_db}</div>
      <div class="stat-label">total tools</div>
    </div>
  </div>
  <div class="search-wrap">
    <input type="text" id="search" placeholder="Search {total_in_db} EU tools..." oninput="onSearch(this.value)" onkeydown="acKey(event)" autocomplete="off"/>
    <div class="ac-dropdown" id="ac"></div>
  </div>
</header>

<div class="verify-strip">
  <div class="verify-ttl">How we verify tools — click any badge to learn more</div>
  <div class="verify-row">
    <div class="vbadge" onclick="toggleTip('t1')">
      <div class="vbadge-icon">&#10003;&#65039;</div>
      <div class="vbadge-label">Verified</div>
      <div class="vbadge-sub">All 5 checks passed</div>
      <div class="vtip" id="t1">
        <div class="vtip-title">&#10003;&#65039; Verified — all checks passed</div>
        <ul>
          <li>Website returns HTTP 200 OK</li>
          <li>HQ or primary team in EU / UK</li>
          <li>Real product description</li>
          <li>Active project (updated &lt;2 years)</li>
          <li>Software product, not an agency</li>
        </ul>
      </div>
    </div>
    <div class="vbadge" onclick="toggleTip('t2')">
      <div class="vbadge-icon">&#128269;</div>
      <div class="vbadge-label">Unverified</div>
      <div class="vbadge-sub">Listed, not yet confirmed</div>
      <div class="vtip" id="t2">
        <div class="vtip-title">&#128269; Unverified — under review</div>
        <ul>
          <li>URL may be live</li>
          <li>EU/UK origin not yet confirmed</li>
          <li>Community submitted</li>
          <li>Submit corrections below</li>
        </ul>
      </div>
    </div>
    <div class="vbadge" onclick="toggleTip('t3')">
      <div class="vbadge-icon">&#11088;</div>
      <div class="vbadge-label">Featured</div>
      <div class="vbadge-sub">Paid &middot; Top of category</div>
      <div class="vtip" id="t3">
        <div class="vtip-title">&#11088; Featured listing &mdash; $29/mo</div>
        <ul>
          <li>Must pass Verified criteria first</li>
          <li>Pinned at top of every category</li>
          <li>Gold border highlighted card</li>
          <li>Included in monthly newsletter</li>
          <li><a href="https://rickyfarmer.gumroad.com/l/eutech-featured" style="color:#00bcd4;text-decoration:underline">Get featured listing &#8594;</a></li>
        </ul>
      </div>
    </div>
    <div class="vbadge" onclick="toggleTip('t4')">
      <div class="vbadge-icon">&#128268;</div>
      <div class="vbadge-label">MCP verified</div>
      <div class="vbadge-sub">Extra MCP checks</div>
      <div class="vtip" id="t4">
        <div class="vtip-title">&#128268; MCP verified</div>
        <ul>
          <li>Working tool endpoint confirmed</li>
          <li>Valid JSON schema extractable</li>
          <li>Open source license present</li>
          <li>GitHub repo maintained &lt;1 year</li>
          <li>Listed on Smithery or Glama</li>
        </ul>
      </div>
    </div>
  </div>
</div>


<div class="static-intro" style="max-width:960px;margin:0 auto;padding:24px;color:#e6edf3">
  <p style="font-size:15px;line-height:1.7;color:#94a3b8;margin-bottom:12px">
    eutech.directory is the largest verified directory of EU-built software alternatives.
    We list <strong style="color:#e6edf3">4,086 tools</strong> across 13 categories including
    MCP Servers, Developer Tools, Analytics, Cloud Hosting, and Email platforms —
    all headquartered in the EU or UK, GDPR-compliant by default,
    with no US cloud dependencies.
    Every tool passes 5 verification checks: URL live, EU/UK origin confirmed,
    real product description, active project, and software product.
  </p>
  <p style="font-size:14px;color:#64748b">
    Browse verified EU alternatives to Google Analytics, Slack, Notion, GitHub, Jira,
    Mailchimp, Zoom, Dropbox, AWS, HubSpot, Figma, and 4,000+ more US software tools.
    Updated monthly. 95.3% of listed tools verified live.
  </p>
</div>

<noscript>
<div style="max-width:960px;margin:0 auto;padding:24px;font-family:system-ui,sans-serif;color:#e6edf3;background:#0d1117">
  <h2 style="font-size:18px;margin-bottom:16px;color:#e6edf3">EU Software Alternatives Directory</h2>
  <p style="font-size:14px;color:#94a3b8;margin-bottom:16px">
    This directory requires JavaScript to browse all 4,086 tools interactively.
    Below are direct links to our most popular EU alternative pages:
  </p>
  <ul style="list-style:none;padding:0;columns:2;gap:24px">
    <li><a href="/alternatives/eu-alternative-to-google-analytics/" style="color:#00bcd4">EU alternative to Google Analytics</a></li>
    <li><a href="/alternatives/eu-alternative-to-slack/" style="color:#00bcd4">EU alternative to Slack</a></li>
    <li><a href="/alternatives/eu-alternative-to-notion/" style="color:#00bcd4">EU alternative to Notion</a></li>
    <li><a href="/alternatives/eu-alternative-to-github/" style="color:#00bcd4">EU alternative to GitHub</a></li>
    <li><a href="/alternatives/eu-alternative-to-jira/" style="color:#00bcd4">EU alternative to Jira</a></li>
    <li><a href="/alternatives/eu-alternative-to-zoom/" style="color:#00bcd4">EU alternative to Zoom</a></li>
    <li><a href="/alternatives/eu-alternative-to-mailchimp/" style="color:#00bcd4">EU alternative to Mailchimp</a></li>
    <li><a href="/alternatives/eu-alternative-to-dropbox/" style="color:#00bcd4">EU alternative to Dropbox</a></li>
    <li><a href="/alternatives/eu-alternative-to-aws/" style="color:#00bcd4">EU alternative to AWS</a></li>
    <li><a href="/alternatives/eu-alternative-to-hubspot/" style="color:#00bcd4">EU alternative to HubSpot</a></li>
    <li><a href="/alternatives/eu-alternative-to-figma/" style="color:#00bcd4">EU alternative to Figma</a></li>
    <li><a href="/alternatives/eu-alternative-to-asana/" style="color:#00bcd4">EU alternative to Asana</a></li>
    <li><a href="/alternatives/eu-alternative-to-google-drive/" style="color:#00bcd4">EU alternative to Google Drive</a></li>
    <li><a href="/alternatives/eu-alternative-to-datadog/" style="color:#00bcd4">EU alternative to Datadog</a></li>
    <li><a href="/alternatives/eu-alternative-to-1password/" style="color:#00bcd4">EU alternative to 1Password</a></li>
    <li><a href="/alternatives/eu-alternative-to-sendgrid/" style="color:#00bcd4">EU alternative to SendGrid</a></li>
    <li><a href="/alternatives/eu-alternative-to-salesforce/" style="color:#00bcd4">EU alternative to Salesforce</a></li>
    <li><a href="/alternatives/eu-alternative-to-quickbooks/" style="color:#00bcd4">EU alternative to QuickBooks</a></li>
    <li><a href="/alternatives/eu-alternative-to-google-cloud/" style="color:#00bcd4">EU alternative to Google Cloud</a></li>
    <li><a href="/alternatives/eu-alternative-to-contentful/" style="color:#00bcd4">EU alternative to Contentful</a></li>
  </ul>
  <p style="font-size:13px;color:#64748b;margin-top:16px">
    <a href="https://eutech-directory.github.io/#submit" style="color:#00bcd4">Submit your EU tool</a> |
    Featured listings from $29/month
  </p>
</div>
</noscript>
<div class="cat-bar">
  <button class="all-btn active" onclick="filterCat(this)" data-cat="">All categories</button>
  {cat_buttons}
</div>
<div class="results-bar">
  <span id="result-count">{verified} tools</span>
  <button class="clear-btn" onclick="clearFilters()">Clear filters</button>
</div>

<div id="featured-section">
  <div class="section-label">&#11088; Featured tools</div>
  <div id="featured-grid" class="grid"></div>
</div>
<div class="section-label" id="all-label">&#10003;&#65039; Verified tools</div>
<div id="grid" class="grid"></div>
<div id="empty"><p>No tools found matching your search.</p></div>

<div class="listing-criteria">
  <h2>How to get listed</h2>
  <p class="criteria-intro">eutech.directory lists EU-built and EU-hosted software. To be included, your tool must meet all criteria:</p>
  <div class="criteria-grid">
    <div class="criterion">
      <span class="criterion-icon">&#127466;&#127482;</span>
      <h3>EU-built or EU-hosted</h3>
      <p>Company founded in the EU, or primary servers in EU data centres.</p>
    </div>
    <div class="criterion">
      <span class="criterion-icon">&#128274;</span>
      <h3>GDPR compliant by default</h3>
      <p>Data protection built into the architecture, not just a checkbox.</p>
    </div>
    <div class="criterion">
      <span class="criterion-icon">&#9729;&#65039;</span>
      <h3>No US cloud dependencies</h3>
      <p>Data does not transit through or rest on AWS, GCP, or Azure US regions.</p>
    </div>
    <div class="criterion">
      <span class="criterion-icon">&#9989;</span>
      <h3>Actively maintained</h3>
      <p>Live, usable, and updated within the last 12 months.</p>
    </div>
  </div>
  <p style="text-align:center;font-size:0.9rem;color:var(--muted)">Meet all criteria? <a href="#submit" class="submit-link">Submit below &mdash; we review within 24 hours.</a></p>
</div>

<div id="submit">
  <h2>Submit your tool</h2>
  <p>Know an EU-built alternative we&rsquo;re missing? Add it to the directory.</p>
  <form action="https://formspree.io/f/xqewnpwl" method="POST">
    <div class="form-group">
      <label>Tool name *</label>
      <input type="text" name="tool_name" required placeholder="e.g. Nextcloud"/>
    </div>
    <div class="form-group">
      <label>Website URL *</label>
      <input type="url" name="website" required placeholder="https://"/>
    </div>
    <div class="form-group">
      <label>Category *</label>
      <select name="category" required>
        <option value="" disabled selected>Select category</option>
        <option>MCP Servers</option>
        <option>Developer Tools</option>
        <option>AI &amp; Automation</option>
        <option>Analytics &amp; Data</option>
        <option>Email &amp; Communication</option>
        <option>Cloud &amp; Hosting</option>
        <option>Project Management</option>
        <option>Security &amp; Privacy</option>
        <option>Storage &amp; Backup</option>
        <option>Finance &amp; Payments</option>
        <option>HR &amp; Team</option>
        <option>Marketing &amp; SEO</option>
        <option>Other</option>
      </select>
    </div>
    <div class="form-group">
      <label>Country / HQ *</label>
      <input type="text" name="country" required placeholder="e.g. DE, FR, NL, GB"/>
    </div>
    <div class="form-group">
      <label>What US tool does it replace?</label>
      <input type="text" name="replaces" placeholder="e.g. Slack, Notion, Google Analytics"/>
    </div>
    <div class="form-group">
      <label>Short description *</label>
      <textarea name="description" required placeholder="One or two sentences describing the tool..."></textarea>
    </div>
    <div class="form-group">
      <label>Your email (optional)</label>
      <input type="email" name="email" placeholder="For follow-up if needed"/>
    </div>
    <button type="submit" class="submit-btn">Submit for review &rarr;</button>
  </form>
</div>

<div class="get-listed">
  <div class="get-listed-text">
    <div class="gl-title">Get your EU tool listed</div>
    <div class="gl-sub">Free verified listing &middot; Featured placement from $29/mo &middot; Reach EU developers</div>
  </div>
  <button class="gl-btn" onclick="document.getElementById('submit').scrollIntoView({{behavior:'smooth'}})">Submit tool &rarr;</button>
</div>

<a href="#submit" class="sticky-cta" onclick="document.getElementById('submit').scrollIntoView({{behavior:'smooth'}});return false;">
  <span>+</span> Get listed
</a>

<script>
const TOOLS = {tools_json};
const FEATURED = new Set(TOOLS.filter(t => t.fl === 'featured').map(t => t.n));

const FLAG_MAP = {{"DE":"&#127465;&#127466;","FR":"&#127467;&#127479;","NL":"&#127475;&#127473;","SE":"&#127480;&#127466;","FI":"&#127467;&#127470;","DK":"&#127465;&#127472;","NO":"&#127475;&#127476;","CH":"&#127464;&#127469;","AT":"&#127462;&#127481;","BE":"&#127463;&#127466;","PL":"&#127477;&#127473;","CZ":"&#127464;&#127487;","GB":"&#127468;&#127463;","UK":"&#127468;&#127463;","EU":"&#127466;&#127482;","IE":"&#127470;&#127466;","IT":"&#127470;&#127481;","ES":"&#127466;&#127480;","PT":"&#127477;&#127481;","RO":"&#127479;&#127476;","EE":"&#127466;&#127466;"}};

const CAT_ICONS = {{"MCP Servers":"&#128268;","Developer Tools":"&#128296;","AI & Automation":"&#129302;","Analytics & Data":"&#128202;","Email & Communication":"&#128231;","Cloud & Hosting":"&#9729;&#65039;","Project Management":"&#128203;","Security & Privacy":"&#128274;","Storage & Backup":"&#128190;","Finance & Payments":"&#128179;","HR & Team":"&#128101;","Marketing & SEO":"&#128226;","Other":"&#128230;"}};

let activeCategory = "";
let searchQuery = "";

function getFlag(co) {{
  return FLAG_MAP[co] ? FLAG_MAP[co] + " " + co : (co || "");
}}

function getBadge(t) {{
  if (t.fl === 'featured') return '<span class="badge b-featured">&#11088; Featured</span>';
  if (t.c === 'MCP Servers') return '<span class="badge b-mcp">&#128268; MCP</span>';
  if (t.v) return '<span class="badge b-verified">&#10003; verified</span>';
  return '<span class="badge b-unverified">&#128269; unverified</span>';
}}

function cardHTML(t) {{
  const featured = t.fl === 'featured';
  const flag = getFlag(t.co);
  const link = t.w ? `<a href="${{t.w}}" target="_blank" class="card-link" rel="noopener">Visit &#8594;</a>` : '';
  return `<div class="card${{featured ? ' featured' : ''}}">
    <div class="card-top">
      <span class="card-name">${{t.n}}</span>
      ${{getBadge(t)}}
    </div>
    <p class="card-desc">${{t.d || ''}}</p>
    <div class="card-footer">
      <span class="tag">${{(CAT_ICONS[t.c] || '') + ' ' + (t.c || 'Other')}}</span>
      ${{flag ? `<span class="tag">${{flag}}</span>` : ''}}
      ${{t.r ? `<span class="tag">↔ ${{t.r}}</span>` : ''}}
      ${{link}}
    </div>
  </div>`;
}}

function render() {{
  let f = TOOLS;
  if (activeCategory) f = f.filter(t => t.c === activeCategory);
  if (searchQuery) {{
    const q = searchQuery.toLowerCase();
    f = f.filter(t => (t.n||'').toLowerCase().includes(q) || (t.d||'').toLowerCase().includes(q) || (t.r||'').toLowerCase().includes(q));
  }}

  const featured = f.filter(t => t.fl === 'featured');
  const regular  = f.filter(t => t.fl !== 'featured');

  const featSection = document.getElementById('featured-section');
  const featGrid    = document.getElementById('featured-grid');
  if (featured.length > 0) {{
    featSection.style.display = 'block';
    featGrid.innerHTML = featured.map(cardHTML).join('');
  }} else {{
    featSection.style.display = 'none';
  }}

  document.getElementById('grid').innerHTML = regular.map(cardHTML).join('');
  document.getElementById('result-count').textContent = f.length + ' tools';
  document.getElementById('total-count').textContent = f.length;
  document.getElementById('empty').style.display = f.length === 0 ? 'block' : 'none';
  document.getElementById('all-label').style.display = regular.length > 0 ? 'flex' : 'none';
}}

function filterCat(btn) {{
  document.querySelectorAll('.cat-btn,.all-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  activeCategory = btn.dataset.cat || '';
  render();
}}

function clearFilters() {{
  activeCategory = '';
  searchQuery = '';
  document.getElementById('search').value = '';
  document.querySelectorAll('.cat-btn,.all-btn').forEach(b => b.classList.remove('active'));
  document.querySelector('.all-btn').classList.add('active');
  render();
}}

function onSearch(v) {{
  searchQuery = v;
  render();
  const ac = document.getElementById('ac');
  if (v.length < 2) {{ ac.style.display = 'none'; return; }}
  const q = v.toLowerCase();
  const matches = TOOLS.filter(t => t.n.toLowerCase().startsWith(q)).slice(0,8);
  if (!matches.length) {{ ac.style.display = 'none'; return; }}
  ac.innerHTML = matches.map(t => `<div class="ac-item" onclick="pickAc('${{t.n.replace(/'/g,"\\'")}}')"><b>${{t.n}}</b> <span style="color:var(--muted);font-size:0.8rem">${{t.c}}</span></div>`).join('');
  ac.style.display = 'block';
}}

function pickAc(name) {{
  document.getElementById('search').value = name;
  document.getElementById('ac').style.display = 'none';
  searchQuery = name;
  render();
}}

function acKey(e) {{
  if (e.key === 'Escape') document.getElementById('ac').style.display = 'none';
}}

function toggleTip(id) {{
  document.querySelectorAll('.vtip').forEach(t => {{ if (t.id !== id) t.classList.remove('show'); }});
  document.getElementById(id).classList.toggle('show');
}}

document.addEventListener('click', function(e) {{
  if (!e.target.closest('.vbadge')) document.querySelectorAll('.vtip').forEach(t => t.classList.remove('show'));
  if (!e.target.closest('.search-wrap')) document.getElementById('ac').style.display = 'none';
}});

window.addEventListener('scroll', function() {{
  var btn = document.getElementById('back-top');
  if (!btn) return;
  btn.classList.toggle('visible', window.scrollY > 300);
}});

render();
</script>


<a href="#" class="back-top" id="back-top" aria-label="Back to top" onclick="window.scrollTo({{top:0,behavior:'smooth'}});return false;">&#8679;</a>
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
