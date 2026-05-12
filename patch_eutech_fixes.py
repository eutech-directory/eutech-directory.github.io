"""
Fixes:
1. Featured tooltip email link — wraps mailto in proper anchor
2. Adds back-to-top button that appears after 400px scroll
"""
from pathlib import Path
import re

f = Path(r"C:\Users\USER\NANO\outputs\eutech-directory\build_eutech_index.py")
src = f.read_text(encoding="utf-8")
original = src

# ── Fix 1: Email link in featured tooltip ─────────────────────────────────────
# The mailto link inside the f-string tooltip needs proper href
old_email = '''<li><a href="mailto:ricky.farmerai@gmail.com" style="color:#00bcd4">Email to get listed</a></li>'''
new_email = '''<li><a href="mailto:ricky.farmerai@gmail.com?subject=Featured%20Listing%20eutech.directory&body=Hi%2C%20I%20would%20like%20to%20get%20my%20tool%20featured%20on%20eutech.directory" style="color:#00bcd4;text-decoration:underline" onclick="window.location.href=this.href;return false;">Email to get listed &#8594;</a></li>'''

if old_email in src:
    src = src.replace(old_email, new_email, 1)
    print("Fix 1 applied: featured tooltip email link fixed")
else:
    # Try alternate — the link might be slightly different
    idx = src.find("mailto:ricky.farmerai@gmail.com")
    if idx != -1:
        print(f"Found mailto at {idx}, context:")
        print(repr(src[idx-50:idx+100]))
    else:
        print("Fix 1 SKIP: mailto not found in builder — will patch index.html directly")

# ── Fix 2: Back to top button CSS ─────────────────────────────────────────────
back_top_css = """
    /* Back to top button */
    .back-top {{
      position: fixed; bottom: 80px; right: 24px; z-index: 998;
      background: var(--surface); border: 1px solid var(--border);
      color: var(--muted); width: 42px; height: 42px;
      border-radius: 50%; display: flex; align-items: center;
      justify-content: center; cursor: pointer; font-size: 20px;
      font-weight: 300; line-height: 1;
      transition: all .2s; opacity: 0; pointer-events: none;
      box-shadow: 0 2px 12px rgba(0,0,0,0.3);
      text-decoration: none;
    }}
    .back-top.visible {{ opacity: 1; pointer-events: auto; }}
    .back-top:hover {{
      background: var(--accent); border-color: var(--accent);
      color: #000; transform: translateY(-2px);
      box-shadow: 0 4px 16px rgba(0,188,212,0.3);
    }}"""

# Find the media query to insert CSS before it
target_css = "    @media (max-width: 600px)"
if target_css in src and ".back-top {" not in src and ".back-top {{" not in src:
    src = src.replace(target_css, back_top_css + "\n    @media (max-width: 600px)", 1)
    print("Fix 2a applied: back-to-top CSS added")
elif ".back-top {{" in src:
    print("Fix 2a SKIP: back-to-top CSS already present")
else:
    print("Fix 2a FAIL: CSS target not found")

# ── Fix 3: Back to top HTML button ────────────────────────────────────────────
back_top_html = """<a href="#" class="back-top" id="back-top" title="Back to top" aria-label="Back to top">&#8679;</a>
</body>"""

if "back-top" not in src:
    if "</body>" in src:
        src = src.replace("</body>", back_top_html, 1)
        print("Fix 2b applied: back-to-top button HTML added")
    else:
        print("Fix 2b FAIL: </body> not found")
else:
    print("Fix 2b SKIP: back-to-top button already present")

# ── Fix 4: Back to top scroll JS ──────────────────────────────────────────────
scroll_js = """
// Back to top visibility
window.addEventListener('scroll', function() {{
  var btn = document.getElementById('back-top');
  if (btn) {{
    if (window.scrollY > 400) {{
      btn.classList.add('visible');
    }} else {{
      btn.classList.remove('visible');
    }}
  }}
}});

render();"""

if "window.scrollY > 400" not in src:
    # Find render() call and replace with scroll JS + render()
    if "\nrender();" in src:
        src = src.replace("\nrender();", scroll_js, 1)
        print("Fix 2c applied: scroll JS added")
    elif "render();" in src:
        src = src.replace("render();", scroll_js.strip(), 1)
        print("Fix 2c applied: scroll JS added (alternate)")
    else:
        print("Fix 2c FAIL: render() not found")
else:
    print("Fix 2c SKIP: scroll JS already present")

# ── Save ───────────────────────────────────────────────────────────────────────
f.write_text(src, encoding="utf-8")

# ── Verify syntax ──────────────────────────────────────────────────────────────
try:
    compile(src, str(f), 'exec')
    print("\nSyntax OK ✓")
    print("Run: cd C:\\Users\\USER\\NANO\\outputs\\eutech-directory && python build_eutech_index.py")
except SyntaxError as e:
    print(f"\nSyntax ERROR at line {e.lineno}: {e.msg}")
    # Revert
    f.write_text(original, encoding="utf-8")
    print("Reverted to original")
    lines = src.splitlines()
    start = max(0, e.lineno - 3)
    end   = min(len(lines), e.lineno + 3)
    for i, line in enumerate(lines[start:end], start=start+1):
        mark = ">>>" if i == e.lineno else "   "
        print(f"{mark} {i:4}: {line[:100]}")
