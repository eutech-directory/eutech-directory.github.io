"""
build_pages.py - builds the tool pages (tools/<name>/), category pages (category/<name>/) and sitemap.xml
from data/tools.json. Called by build_site.py, so GitHub runs it automatically when data/ changes.

    python build_pages.py

Only listed tools (verified = true, not MCP servers) get a page. Pages of tools that are no longer listed
are removed, so the site never shows a tool that failed the country check.
"""
import html as _h
import json
import re
import shutil
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = "https://eutech.directory"
MCP_CAT = "MCP Servers"
ALWAYS_HOME = {"Legis-Link MCP"}
OPEN_LABEL = "Open source (self-hosted)"
MARK = "<!-- built by build_pages.py -->"
CF = ("<!-- Cloudflare Web Analytics --><script type='module' src='https://static.cloudflareinsights.com/beacon.min.js' "
      "data-cf-beacon='{\"token\": \"c87f4229eb7e44a19c5e152941ca0275\"}'></script><!-- End Cloudflare Web Analytics -->")
HEAD_ICONS = ('<link rel="icon" href="/favicon.ico" sizes="32x32"><link rel="icon" href="/favicon.svg" type="image/svg+xml">'
              '<link rel="apple-touch-icon" href="/apple-touch-icon.png"><link rel="manifest" href="/site.webmanifest">'
              '<meta name="theme-color" content="#0B3D91">')


def slug(s):
    return re.sub(r"[^a-z0-9]", "-", (s or "").lower()).strip("-")


def fix_text(s):
    s = s or ""
    if "Ã" in s or "Â" in s:
        try:
            s = s.encode("latin-1").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass
    return s.strip()


def e(s):
    return _h.escape(s or "", quote=True)


def page(title, desc, path, body, jsonld=None):
    parts = []
    for j in (jsonld or []):
        parts.append('<script type="application/ld+json">' + json.dumps(j, ensure_ascii=False).replace("</", "<\\/") + "</script>")
    ld = "".join(parts)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
{MARK}
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{BASE}{path}">
<meta property="og:site_name" content="eutech.directory">
<link rel="canonical" href="{BASE}{path}">
<link rel="stylesheet" href="/style.css">
{ld}
{HEAD_ICONS}
</head>
<body>
<nav><a href="/">eutech.directory</a> &mdash; European software directory</nav>
<main>
{body}
</main>
<footer>
  <p>eutech.directory &mdash; {date.today().year} &mdash; <a href="/">Browse all tools</a> &middot; <a href="/mcp-servers/">MCP servers</a> &middot; <a href="/privacy.html">Privacy</a></p>
  <p>A European company does not automatically mean your data stays in Europe. Check where each provider stores data before you switch.</p>
</footer>
{CF}
</body>
</html>
"""


def origin_html(t):
    c = t.get("country") or ""
    src = t.get("country_source") or ""
    if t["name"] in ALWAYS_HOME:
        return f"<p><strong>Regions covered:</strong> {e(c)}</p>" if c else ""
    if c == OPEN_LABEL:
        return "<p><strong>Type:</strong> open-source project you host yourself. There is no company behind it to check.</p>"
    if not c:
        return ""
    proof = f' (<a href="{e(src)}" rel="noopener nofollow" target="_blank">source checked</a>)' if src.startswith("http") else ""
    return f"<p><strong>Company based in:</strong> {e(c)}{proof}</p>"


def origin_answer(t):
    c = t.get("country") or ""
    if c == OPEN_LABEL:
        return f"{t['name']} is an open-source project that you host yourself, so where your data is stored depends on where you run it."
    if c and t["name"] not in ALWAYS_HOME:
        return (f"The company behind {t['name']} is based in {c}. Where your data is stored can still depend on the plan "
                f"and hosting region you choose, so check the provider's own documentation.")
    return ""


def tool_page(t, cat_slug, others):
    cat_url = "/mcp-servers/" if (t.get("category") == MCP_CAT) else f"/category/{cat_slug}/"
    name, cat = t["name"], t.get("category") or "Other"
    desc = fix_text(t.get("description"))
    if not desc or desc == name:
        desc = f"{name} is listed on eutech.directory under {cat}."
    path = f"/tools/{slug(name)}/"
    title = (f"{name} - MCP server | eutech.directory" if cat == MCP_CAT
             else f"{name} - European {cat} software | eutech.directory")
    replaces = (t.get("replaces") or "").strip()
    rep = f"<p><strong>Alternative to:</strong> {e(replaces)}</p>" if replaces else ""
    site = t.get("website") or ""
    visit = f'<p><a href="{e(site)}" rel="noopener" target="_blank">Visit {e(name)} &rarr;</a></p>' if site.startswith("http") else ""
    ans = origin_answer(t)
    faq = (f'<section class="faq"><h2>Where is {e(name)} based?</h2><p>{e(ans)}</p></section>') if ans else ""
    sim = "".join(f'<li><a href="/tools/{slug(o["name"])}/">{e(o["name"])}</a></li>' for o in others)
    sim_html = "" if not others else (f'<section><h2>Other {e(cat)} tools</h2><ul>{sim}</ul>'
                f'<p><a href="{cat_url}">All {e(cat)} &rarr;</a></p></section>')
    body = f"""  <div class="breadcrumb"><a href="/">Home</a> &rarr; <a href="{cat_url}">{e(cat)}</a> &rarr; {e(name)}</div>
  <h1>{e(name)}</h1>
  <div class="badges"><span class="badge">{e(cat)}</span></div>
  <p class="description">{e(desc)}</p>
  {origin_html(t)}
  {rep}
  {visit}
  {faq}
  {sim_html}"""
    ld = [{"@context": "https://schema.org", "@type": "SoftwareApplication", "name": name, "url": site or f"{BASE}{path}",
           "applicationCategory": cat, "description": desc}]
    if ans:
        ld.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": f"Where is {name} based?", "acceptedAnswer": {"@type": "Answer", "text": ans}}]})
    return path, page(title, desc[:155], path, body, ld)


def category_page(cat, cat_slug, items):
    n = len(items)
    path = f"/category/{cat_slug}/"
    title = f"European {cat} software ({n} tools) | eutech.directory"
    desc = f"{n} {cat} tools from European companies and open-source projects, each with its home country checked."
    cards = []
    for t in items:
        c = t.get("country") or ""
        meta = "Open source, self-hosted" if c == OPEN_LABEL else (c if t["name"] not in ALWAYS_HOME else "")
        d = fix_text(t.get("description"))
        d = "" if d == t["name"] else d
        site = t.get("website") or ""
        visit = f"<a href='{e(site)}' rel='noopener' target='_blank'>Visit &rarr;</a>" if site.startswith("http") else ""
        cards.append(f"""  <div class="tool-card">
    <h3><a href="/tools/{slug(t['name'])}/">{e(t['name'])}</a></h3>
    <p class="meta">{e(meta)}</p>
    <p>{e(d[:200])}</p>
    {visit}
  </div>""")
    body = f"""  <div class="breadcrumb"><a href="/">Home</a> &rarr; {e(cat)}</div>
  <h1>European {e(cat)} software</h1>
  <p class="lead">{n} tools. Each company's home country was checked on its own website; open-source projects are marked as such.</p>
  <div class="tool-grid">
{chr(10).join(cards)}
  </div>"""
    ld = [{"@context": "https://schema.org", "@type": "ItemList", "name": f"European {cat} software", "url": f"{BASE}{path}",
           "numberOfItems": n, "itemListElement": [
               {"@type": "ListItem", "position": i + 1, "name": t["name"], "url": f"{BASE}/tools/{slug(t['name'])}/"}
               for i, t in enumerate(items[:50])]}]
    return path, page(title, desc, path, body, ld)


def write(path, text):
    p = ROOT / path.strip("/") / "index.html"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def main():
    data = json.loads((ROOT / "data" / "tools.json").read_text(encoding="utf-8"))
    hl = json.loads((ROOT / "data" / "highlights.json").read_text(encoding="utf-8"))
    rank = {n: 0 for n in hl.get("featured", [])}
    rank.update({n: 1 for n in hl.get("picks", []) if n not in rank})
    listed, seen = [], set()
    for t in data["tools"]:
        if not t.get("verified"):
            continue
        if t.get("category") == MCP_CAT and t.get("name") not in ALWAYS_HOME:
            continue
        s = slug(t.get("name"))
        if not s or s in seen:
            continue
        seen.add(s)
        listed.append(t)
    listed.sort(key=lambda t: (rank.get(t["name"], 2), t["name"].lower()))

    by_cat = {}
    for t in listed:
        by_cat.setdefault(t.get("category") or "Other", []).append(t)

    urls = ["/", "/mcp-servers/"]
    keep_tools, keep_cats = set(), set()
    for cat, items in by_cat.items():
        cs = slug(cat)
        if cat != MCP_CAT:
            keep_cats.add(cs)
            path, text = category_page(cat, cs, items)
            write(path, text)
            urls.append(path)
        for i, t in enumerate(items):
            others = [items[(i + k) % len(items)] for k in range(1, min(7, len(items)))]
            path, text = tool_page(t, cs, others)
            write(path, text)
            keep_tools.add(slug(t["name"]))
            urls.append(path)

    removed = 0
    for folder, keep in (("tools", keep_tools), ("category", keep_cats)):
        base = ROOT / folder
        if base.is_dir():
            for d in base.iterdir():
                if d.is_dir() and d.name not in keep:
                    shutil.rmtree(d)
                    removed += 1

    alt = ROOT / "alternatives"
    if alt.is_dir():
        urls += sorted(f"/alternatives/{d.name}/" for d in alt.iterdir() if (d / "index.html").exists())
    today = date.today().isoformat()
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sm += [f"  <url><loc>{BASE}{u}</loc><lastmod>{today}</lastmod></url>" for u in urls]
    sm.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(sm) + "\n", encoding="utf-8")
    print(f"Built {len(keep_tools)} tool pages, {len(keep_cats)} category pages, sitemap.xml ({len(urls)} URLs); "
          f"removed {removed} old pages")


if __name__ == "__main__":
    main()
