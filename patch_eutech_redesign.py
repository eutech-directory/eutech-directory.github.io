#!/usr/bin/env python3
"""
eutech.directory — Full Redesign Patch
=======================================
Updates build_eutech_index.py with:
1. New dark theme with cyan (#00bcd4) accent
2. Featured tools section pinned at top of every category
3. Clickable verification badges with tooltips
4. Country flags on every card
5. "Get listed" banner always visible
6. Interactive category filter
7. CNAME file for eutech.directory domain

Run: python patch_eutech_redesign.py
"""
from pathlib import Path
import ast

BUILDER = Path(r"C:\Users\USER\NANO\outputs\eutech-directory\build_eutech_index.py")
src = BUILDER.read_text(encoding="utf-8")
original = src

# ── Country flag map ───────────────────────────────────────────────────────────
FLAG_MAP = {
    "DE": "🇩🇪", "FR": "🇫🇷", "NL": "🇳🇱", "SE": "🇸🇪", "FI": "🇫🇮",
    "DK": "🇩🇰", "NO": "🇳🇴", "CH": "🇨🇭", "AT": "🇦🇹", "BE": "🇧🇪",
    "PL": "🇵🇱", "CZ": "🇨🇿", "HU": "🇭🇺", "RO": "🇷🇴", "PT": "🇵🇹",
    "ES": "🇪🇸", "IT": "🇮🇹", "IE": "🇮🇪", "LU": "🇱🇺", "EE": "🇪🇪",
    "GB": "🇬🇧", "UK": "🇬🇧", "EU": "🇪🇺",
}

CATEGORY_ICONS = {
    "MCP Servers": "🔌",
    "Developer Tools": "🛠",
    "AI & Automation": "🤖",
    "Analytics & Data": "📊",
    "Email & Communication": "📧",
    "Cloud & Hosting": "☁️",
    "Project Management": "📋",
    "Security & Privacy": "🔒",
    "Storage & Backup": "💾",
    "Finance & Payments": "💳",
    "HR & Team": "👥",
    "Marketing & SEO": "📣",
    "Other": "📦",
}

# ── New CSS replacing the old style block ─────────────────────────────────────
NEW_CSS = """
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

    @media (max-width: 600px) {{
      .logo {{ font-size: 1.8rem; }}
      .stat-num {{ font-size: 1.4rem; }}
      .grid {{ grid-template-columns: 1fr; padding: 8px 12px; }}
      .verify-row {{ grid-template-columns: repeat(2, 1fr); }}
    }}
"""

# ── New build_html function ────────────────────────────────────────────────────
NEW_BUILD_HTML = '''def build_html(tools, tools_json, cat_buttons, total_in_db):
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
''' + NEW_CSS + '''
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
          <li><a href="mailto:ricky.farmerai@gmail.com" style="color:#00bcd4">Email to get listed</a></li>
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

<a href="#submit" class="sticky-cta">
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
  ac.innerHTML = matches.map(t => `<div class="ac-item" onclick="pickAc('${{t.n.replace(/'/g,"\\\\'")}}')"><b>${{t.n}}</b> <span style="color:var(--muted);font-size:0.8rem">${{t.c}}</span></div>`).join('');
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

render();
</script>
</body>
</html>"""
'''

# Find and replace the old build_html function
import re
# Find start of build_html
start_match = re.search(r'\ndef build_html\(', src)
if not start_match:
    print("ERROR: build_html not found")
    exit(1)

# Find the next top-level function after build_html
next_fn = re.search(r'\ndef \w+\(', src[start_match.end():])
if next_fn:
    end_pos = start_match.end() + next_fn.start()
    src = src[:start_match.start()+1] + NEW_BUILD_HTML + "\n\n" + src[end_pos+1:]
    print("build_html replaced")
else:
    # build_html is the last function — replace to end of file
    src = src[:start_match.start()+1] + NEW_BUILD_HTML
    print("build_html replaced (last function)")

# ── Also update tools JSON to include country, replaces, featured flag ─────────
old_json_line = '''            "c":  (t["category"] or "Other"),'''
new_json_line = '''            "c":  (t["category"] or "Other"),
            "co": (t["country"] or ""),
            "r":  (t["replaces_us_tool"] or "")[:30] if t.get("replaces_us_tool") else "",
            "fl": "featured" if (t.get("upvotes") or 0) >= 5 else "",'''

if old_json_line in src:
    src = src.replace(old_json_line, new_json_line, 1)
    print("JSON fields updated: country, replaces, featured flag")
else:
    print("WARN: JSON line not found — check manually")

# ── Save ───────────────────────────────────────────────────────────────────────
BUILDER.write_text(src, encoding="utf-8")

# ── Create CNAME file ──────────────────────────────────────────────────────────
cname = Path(r"C:\Users\USER\NANO\outputs\eutech-directory\CNAME")
cname.write_text("eutech.directory\n", encoding="utf-8")
print("CNAME created: eutech.directory")

# ── Syntax check ──────────────────────────────────────────────────────────────
try:
    compile(src, str(BUILDER), 'exec')
    print("\nSyntax OK ✓")
    print("Run: python build_eutech_index.py")
except SyntaxError as e:
    print(f"\nSyntax ERROR at line {e.lineno}: {e.msg}")
    lines = src.splitlines()
    start = max(0, e.lineno-3)
    end   = min(len(lines), e.lineno+3)
    for i, line in enumerate(lines[start:end], start=start+1):
        mark = ">>>" if i == e.lineno else "   "
        print(f"{mark} {i:4}: {line[:100]}")
