"""
export_tools_json.py - run on the PC that holds the eutech database.
Reads the eu_alternatives table and refreshes data/tools.json, which the site is built from.

    python export_tools_json.py

Needs EUTECH_DB_URL (set on this PC). Never commit the database address or password.

The country checks live in data/tools.json, not only in the database. For every tool that is already in
data/tools.json, this script KEEPS its country, its proof link (country_source) and whether it is listed
(verified). Only new tools from the database are added with the database values, and they stay hidden
until they pass the country check (python eutech_country_check.py check, then apply).
Featured and Editor's picks live in data/highlights.json.
"""
import json
import os
from datetime import date
from pathlib import Path

import psycopg2
import psycopg2.extras

OUT = Path(__file__).resolve().parent / "data" / "tools.json"


def main():
    url = os.environ.get("EUTECH_DB_URL", "")
    if not url:
        raise SystemExit("EUTECH_DB_URL is not set on this PC")
    old = {}
    if OUT.exists():
        old = {t["name"]: t for t in json.loads(OUT.read_text(encoding="utf-8"))["tools"]}
    conn = psycopg2.connect(url)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM eu_alternatives ORDER BY category, name")
    rows = cur.fetchall()
    conn.close()
    tools, new, kept = [], 0, 0
    seen = set()
    for r in rows:
        name = r.get("name") or ""
        t = {
            "name": name,
            "category": r.get("category") or "Other",
            "country": r.get("country") or "",
            "replaces": r.get("replaces_us_tool") or "",
            "description": r.get("description") or "",
            "website": r.get("website") or "",
            "verified": False,
        }
        if name in old:
            o = old[name]
            t["country"] = o.get("country", t["country"])
            t["verified"] = bool(o.get("verified"))
            if o.get("country_source"):
                t["country_source"] = o["country_source"]
            kept += 1
        elif t["category"] == "MCP Servers":
            t["verified"] = bool(r.get("verified"))
            new += 1
        else:
            new += 1   # new business tool: hidden until the country check passes
        tools.append(t)
        seen.add(name)
    # tools that exist only in tools.json (e.g. added by hand) are kept as they are
    only_json = [o for n, o in old.items() if n not in seen]
    tools += only_json
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps({"exported": date.today().isoformat(), "source": "database + checked countries", "tools": tools},
                              ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"Wrote {OUT}: {len(tools)} tools ({kept} kept their checked country and status, {new} new from the database, "
          f"{len(only_json)} only in tools.json).")
    if new:
        print("New business tools are hidden until checked: python eutech_country_check.py check, review, then apply.")


if __name__ == "__main__":
    main()
