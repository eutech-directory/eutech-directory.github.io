"""
export_tools_json.py - run on the PC that holds the eutech database.
Reads the eu_alternatives table and rewrites data/tools.json, which the site is built from.

    python export_tools_json.py

Needs EUTECH_DB_URL (already set on this PC). Never commit the database address or password.
Featured and Editor's picks are not taken from the database: edit data/highlights.json.
"""
import json
import os
from datetime import date
from pathlib import Path

import psycopg2
import psycopg2.extras


def main():
    url = os.environ.get("EUTECH_DB_URL", "")
    if not url:
        raise SystemExit("EUTECH_DB_URL is not set on this PC")
    conn = psycopg2.connect(url)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM eu_alternatives ORDER BY category, name")
    rows = cur.fetchall()
    conn.close()
    tools = []
    for r in rows:
        tools.append({
            "name": r.get("name") or "",
            "category": r.get("category") or "Other",
            "country": r.get("country") or "",
            "replaces": r.get("replaces_us_tool") or "",
            "description": r.get("description") or "",
            "website": r.get("website") or "",
            "verified": bool(r.get("verified")),
        })
    out = Path(__file__).resolve().parent / "data" / "tools.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"exported": date.today().isoformat(), "source": "database", "tools": tools},
                              ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"Wrote {out}: {len(tools)} tools ({sum(1 for t in tools if t['verified'])} verified)")


if __name__ == "__main__":
    main()
