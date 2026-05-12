"""
Adds back-to-top arrow button to build_eutech_index.py
Appears after user scrolls 400px down, smooth scroll back to top
"""
from pathlib import Path

f = Path(r"C:\Users\USER\NANO\outputs\eutech-directory\build_eutech_index.py")
src = f.read_text(encoding="utf-8")

# CSS for back to top button
css = """
    /* Back to top */
    .back-top {{
      position: fixed; bottom: 80px; right: 24px; z-index: 998;
      background: var(--surface); border: 1px solid var(--border);
      color: var(--muted); width: 40px; height: 40px;
      border-radius: 50%; display: flex; align-items: center;
      justify-content: center; cursor: pointer; font-size: 18px;
      transition: all .2s; opacity: 0; pointer-events: none;
      box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }}
    .back-top.visible {{
      opacity: 1; pointer-events: auto;
    }}
    .back-top:hover {{
      background: var(--accent); border-color: var(--accent);
      color: #000; transform: translateY(-2px);
    }}"""

# HTML button before </body>
btn_html = """<button class="back-top" id="back-top" onclick="window.scrollTo({{top:0,behavior:'smooth'}})" title="Back to top">&#8679;</button>
</body>"""

# JS to show/hide on scroll — add before render() call
scroll_js = """
window.addEventListener('scroll', function() {{
  const btn = document.getElementById('back-top');
  if (btn) btn.classList.toggle('visible', window.scrollY > 400);
}});

render();"""

# Apply patches
if ".back-top {" not in src and ".back-top {{" not in src:
    # Find CSS insertion point — before closing style tag
    target = "    @media (max-width: 600px)"
    if target in src:
        src = src.replace(target, css + "\n    @media (max-width: 600px)", 1)
        print("CSS added")
    else:
        print("WARN: CSS target not found")
else:
    print("CSS already present")

if "back-top" not in src:
    # Add button before </body>
    src = src.replace("</body>", btn_html, 1)
    print("Button HTML added")
else:
    print("Button HTML already present")

if "window.scrollY > 400" not in src:
    src = src.replace("\nrender();", scroll_js, 1)
    print("Scroll JS added")
else:
    print("Scroll JS already present")

f.write_text(src, encoding="utf-8")

# Verify
import py_compile
try:
    py_compile.compile(str(f), doraise=True)
    print("Syntax OK")
except py_compile.PyCompileError as e:
    print(f"Syntax error: {e}")
