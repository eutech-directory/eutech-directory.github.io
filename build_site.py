"""
build_site.py - builds index.html and mcp-servers/index.html from data/ and site_template.html.
No database needed. GitHub runs this automatically when data/ changes (.github/workflows/build.yml).

    python build_site.py
"""
import html as _h
import json
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MCP_CAT = "MCP Servers"
ALWAYS_HOME = {"Legis-Link MCP"}   # stays on the homepage although its category is MCP Servers
CAT_ORDER = ["Project Management", "Developer Tools", "Email & Communication", "Security & Privacy",
             "Analytics & Data", "Storage & Backup", "AI & Automation", "Cloud & Hosting",
             "Finance & Payments", "HR & Team", "Marketing & SEO", "Other"]


def ascii_text(s, n=200):
    return (s or "")[:n].encode("ascii", errors="ignore").decode("ascii").strip()


def main():
    data = json.loads((ROOT / "data" / "tools.json").read_text(encoding="utf-8"))
    hl = json.loads((ROOT / "data" / "highlights.json").read_text(encoding="utf-8"))
    featured, picks = set(hl.get("featured", [])), set(hl.get("picks", []))
    tools = [t for t in data["tools"] if t.get("verified")]
    tools.sort(key=lambda t: ((t.get("category") or "Other"), (t.get("name") or "").lower()))
    home = [t for t in tools if t.get("category") != MCP_CAT or (t.get("name") or "") in ALWAYS_HOME]
    mcp = [t for t in tools if t.get("category") == MCP_CAT and (t.get("name") or "") not in ALWAYS_HOME]

    rows = []
    for t in home:
        name = t.get("name") or ""
        rows.append({"n": name, "c": t.get("category") or "Other", "co": t.get("country") or "",
                     "r": (t.get("replaces") or "")[:30],
                     "fl": "featured" if name in featured else ("pick" if name in picks else ""),
                     "d": ascii_text(t.get("description")), "w": t.get("website") or ""})
    # featured first, then picks, then the rest (same order the live page used)
    rank = {"featured": 0, "pick": 1, "": 2}
    rows.sort(key=lambda r: rank[r["fl"]])
    tools_json = json.dumps(rows, ensure_ascii=True, separators=(",", ":")).replace("</", "<\\/")

    counts = Counter(t.get("category") or "Other" for t in home if t.get("category") != MCP_CAT)
    cats = [c for c in CAT_ORDER if counts.get(c)] + sorted(c for c in counts if c not in CAT_ORDER)
    buttons = []
    for c in cats:
        e = _h.escape(c)
        buttons.append(f'<button class="cat-btn" data-cat="{e}" onclick="filterCat(this)">{e} '
                       f'<span class="cat-count">{counts[c]:,}</span></button>')
    buttons.append('<a class="cat-btn cat-mcp" href="/mcp-servers/" style="text-decoration:none">MCP servers &rarr;</a>')

    month = date.today().strftime("%B %Y")
    page = (ROOT / "site_template.html").read_text(encoding="utf-8")
    values = {
        "{{META_DESC}}": f"Find European alternatives to US software: {len(home):,} tools across {len(cats)} categories, "
                         f"from analytics and chat to hosting and security.",
        "{{HOME}}": f"{len(home):,}", "{{MCP}}": f"{len(mcp):,}", "{{CATS}}": str(len(cats)),
        "{{MONTH_SHORT}}": date.today().strftime("%b %Y"), "{{MONTH}}": month,
        "{{CAT_BUTTONS}}": "\n  ".join(buttons), "{{TOOLS_JSON}}": tools_json,
    }
    for k, v in values.items():
        if k not in page:
            raise SystemExit("Placeholder missing in site_template.html: " + k)
        page = page.replace(k, v)
    (ROOT / "index.html").write_text(page, encoding="utf-8")

    trs = []
    for t in mcp:
        name = _h.escape(t.get("name") or "")
        url = _h.escape(t.get("website") or "", quote=True)
        link = f'<a href="{url}" rel="noopener" target="_blank">{name}</a>' if url else name
        trs.append(f"<tr><td>{link}</td><td>{_h.escape(t.get('country') or '')}</td>"
                   f"<td>{_h.escape(ascii_text(t.get('description')))}</td></tr>")
    mcp_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/><meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>European MCP servers ({len(mcp):,}) - eutech.directory</title>
<meta name="description" content="{len(mcp):,} MCP servers from European developers and companies, kept separate from the eutech.directory software directory. Updated {month}."/>
<link rel="canonical" href="https://eutech.directory/mcp-servers/"/>
<link rel="icon" href="/favicon.ico" sizes="32x32"><link rel="icon" href="/favicon.svg" type="image/svg+xml">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;background:#0d1117;color:#e6edf3;line-height:1.5}}
.wrap{{max-width:1100px;margin:0 auto;padding:24px 16px}}
nav{{display:flex;justify-content:space-between;align-items:center;gap:12px;padding-bottom:16px;border-bottom:1px solid #21262d;margin-bottom:24px}}
.brand{{font-size:20px;font-weight:800;color:#fff;text-decoration:none}}.brand span{{color:#00bcd4}}
h1{{font-size:26px;margin-bottom:8px}}.lead{{color:#94a3b8;margin-bottom:16px}}
input{{width:100%;padding:10px 12px;border-radius:8px;border:1px solid #334155;background:#1e293b;color:#e6edf3;margin-bottom:16px;font-size:15px}}
.tbl{{overflow-x:auto}}table{{width:100%;border-collapse:collapse;font-size:14px}}
th,td{{text-align:left;padding:8px;border-bottom:1px solid #21262d;vertical-align:top}}th{{color:#8b949e;font-weight:600}}
td a{{color:#00bcd4;text-decoration:none}}footer{{margin-top:24px;color:#8b949e;font-size:13px}}footer a{{color:#00bcd4}}
</style>
</head>
<body><div class="wrap">
<nav><a href="/" class="brand">eutech<span>.</span>directory</a><a href="/" style="color:#00bcd4;text-decoration:none;font-size:14px">&larr; European software</a></nav>
<h1>European MCP servers</h1>
<p class="lead">{len(mcp):,} MCP servers from European developers and companies. MCP servers connect AI assistants such as Claude or Cursor to other services. Updated {month}.</p>
<input id="q" type="search" placeholder="Filter by name, country or description..." oninput="f(this.value)" aria-label="Filter MCP servers"/>
<div class="tbl"><table><thead><tr><th>Server</th><th>Country</th><th>Description</th></tr></thead>
<tbody id="rows">
{chr(10).join(trs)}
</tbody></table></div>
<footer>eutech.directory &middot; <a href="/#submit">Submit a tool</a> &middot; <a href="/privacy.html">Privacy</a></footer>
</div>
<script>
function f(v){{v=v.toLowerCase();document.querySelectorAll('#rows tr').forEach(function(r){{r.style.display=r.textContent.toLowerCase().indexOf(v)>-1?'':'none';}});}}
</script>
<!-- Cloudflare Web Analytics --><script type='module' src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{{"token": "c87f4229eb7e44a19c5e152941ca0275"}}'></script><!-- End Cloudflare Web Analytics -->
</body></html>
"""
    (ROOT / "mcp-servers").mkdir(exist_ok=True)
    (ROOT / "mcp-servers" / "index.html").write_text(mcp_html, encoding="utf-8")
    print(f"Built index.html ({len(home):,} tools, {len(cats)} categories) and mcp-servers/index.html ({len(mcp):,} servers)")


if __name__ == "__main__":
    main()
