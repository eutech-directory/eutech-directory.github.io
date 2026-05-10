"""
Patches build_eutech_index.py to permanently add:
1. Verification criteria section after header
2. Sticky "Get listed" button always visible
"""
from pathlib import Path

f = Path(r"C:\Users\USER\NANO\outputs\eutech-directory\build_eutech_index.py")
src = f.read_text(encoding="utf-8")
original = src

# ── Patch 1: Verification section + sticky button CSS in <style> ──────────────
css_patch = """
    /* Verification banner */
    .verify-banner{background:#0d1117;border-top:1px solid #21262d;border-bottom:1px solid #21262d;padding:32px 24px}
    .verify-inner{max-width:1100px;margin:0 auto}
    .verify-title{font-size:11px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:#64748b;margin:0 0 16px}
    .verify-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin-bottom:14px}
    .verify-item{background:#161b22;border:1px solid #21262d;border-radius:10px;padding:14px;transition:border-color .2s}
    .verify-item:hover{border-color:#2563eb55}
    .verify-label{font-size:13px;font-weight:600;color:#e6edf3;margin:0 0 5px}
    .verify-desc{font-size:12px;color:#8b949e;line-height:1.5;margin:0}
    .verify-criteria{background:#161b22;border:1px solid #21262d;border-radius:10px;padding:18px 22px;margin-top:4px}
    .criteria-title{font-size:11px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:#64748b;margin:0 0 12px}
    .criteria-list{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:8px;margin-bottom:14px}
    .criteria-item{display:flex;align-items:flex-start;gap:8px;font-size:13px;color:#8b949e;line-height:1.4}
    /* Sticky get listed button */
    .sticky-cta{position:fixed;bottom:24px;right:24px;z-index:999;background:#2563eb;color:#fff;border:none;border-radius:50px;padding:12px 20px;font-size:13px;font-weight:600;cursor:pointer;box-shadow:0 4px 20px rgba(37,99,235,0.4);transition:all .2s;text-decoration:none;display:flex;align-items:center;gap:8px}
    .sticky-cta:hover{background:#1d4ed8;transform:translateY(-2px);box-shadow:0 6px 24px rgba(37,99,235,0.5)}
    .sticky-cta svg{flex-shrink:0}"""

# Find the closing </style> before </head> and insert CSS before it
old_css = "  </style>\n</head>"
new_css = css_patch + "\n  </style>\n</head>"

if old_css in src:
    src = src.replace(old_css, new_css, 1)
    print("Patch 1a: CSS added")
else:
    print("FAIL 1a: closing style tag not found")
    idx = src.find("</style>")
    print(f"  Found </style> at: {idx}")
    print(f"  Context: {repr(src[idx:idx+30])}")

# ── Patch 2: Verification HTML after </header> ────────────────────────────────
verify_html = """</header>
<div class="verify-banner">
  <div class="verify-inner">
    <p class="verify-title">How we verify tools</p>
    <div class="verify-grid">
      <div class="verify-item">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#4ade80" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom:8px;display:block"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
        <p class="verify-label">Verified</p>
        <p class="verify-desc">URL live &middot; EU/UK origin confirmed &middot; Real description &middot; Active project</p>
      </div>
      <div class="verify-item">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#8b949e" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom:8px;display:block"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        <p class="verify-label">Unverified</p>
        <p class="verify-desc">Listed but origin not yet confirmed. Community submitted.</p>
      </div>
      <div class="verify-item">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#fbbf24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom:8px;display:block"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
        <p class="verify-label">Featured</p>
        <p class="verify-desc">Verified + paid listing. Top of category. <a href="mailto:ricky.farmerai@gmail.com" style="color:#2563eb;text-decoration:none">Get listed &rarr;</a></p>
      </div>
      <div class="verify-item">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#60a5fa" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom:8px;display:block"><path d="M9 3H5a2 2 0 0 0-2 2v4m6-6h10a2 2 0 0 1 2 2v4M9 3v18m0 0h10a2 2 0 0 0 2-2V9M9 21H5a2 2 0 0 1-2-2V9m0 0h18"/></svg>
        <p class="verify-label">MCP verified</p>
        <p class="verify-desc">Working tools &middot; Valid schema &middot; Open source license &middot; Maintained</p>
      </div>
    </div>
    <div class="verify-criteria">
      <p class="criteria-title">Verification criteria</p>
      <div class="criteria-list">
        <div class="criteria-item"><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#4ade80" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink:0;margin-top:2px"><polyline points="20 6 9 17 4 12"/></svg><span>Website returns HTTP 200 OK</span></div>
        <div class="criteria-item"><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#4ade80" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink:0;margin-top:2px"><polyline points="20 6 9 17 4 12"/></svg><span>HQ or primary team in EU / UK</span></div>
        <div class="criteria-item"><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#4ade80" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink:0;margin-top:2px"><polyline points="20 6 9 17 4 12"/></svg><span>Real product description</span></div>
        <div class="criteria-item"><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#4ade80" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink:0;margin-top:2px"><polyline points="20 6 9 17 4 12"/></svg><span>Active project (updated within 2 years)</span></div>
        <div class="criteria-item"><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#4ade80" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink:0;margin-top:2px"><polyline points="20 6 9 17 4 12"/></svg><span>Software product (not agency or consultancy)</span></div>
        <div class="criteria-item" style="font-style:italic;color:#6b7280"><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#60a5fa" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink:0;margin-top:2px"><path d="M9 3H5a2 2 0 0 0-2 2v4m6-6h10a2 2 0 0 1 2 2v4M9 3v18m0 0h10a2 2 0 0 0 2-2V9M9 21H5a2 2 0 0 1-2-2V9m0 0h18"/></svg><span>MCP only: valid schema &middot; open source license &middot; working endpoint</span></div>
      </div>
      <div style="border-top:1px solid #21262d;padding-top:12px;font-size:13px;color:#64748b">Know an EU tool we&rsquo;re missing? <a href="#submit" style="color:#2563eb;text-decoration:none;font-weight:500">Submit it &rarr;</a></div>
    </div>
  </div>
</div>"""

old_header = "</header>\n<div class=\"cat-bar\">"
new_header = verify_html + "\n<div class=\"cat-bar\">"

if old_header in src:
    src = src.replace(old_header, new_header, 1)
    print("Patch 2: verification HTML added after header")
else:
    print("FAIL 2: </header> pattern not found")
    idx = src.find("</header>")
    print(f"  Found at: {idx}, context: {repr(src[idx:idx+40])}")

# ── Patch 3: Sticky Get Listed button before </body> ─────────────────────────
sticky_btn = """<a href="#submit" class="sticky-cta">
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
  Get listed
</a>
</body>"""

old_body = "</body>"
if old_body in src:
    src = src.replace(old_body, sticky_btn, 1)
    print("Patch 3: sticky Get Listed button added")
else:
    print("FAIL 3: </body> not found")

# ── Save and verify ───────────────────────────────────────────────────────────
f.write_text(src, encoding="utf-8")

# Verify patches landed
checks = ["verify-banner", "sticky-cta", "verify-criteria"]
for check in checks:
    status = "OK" if check in src else "MISSING"
    print(f"  Check {check}: {status}")

print("\nDone. Run: python build_eutech_index.py")
