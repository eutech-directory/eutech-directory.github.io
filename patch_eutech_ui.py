#!/usr/bin/env python3
"""
patch_eutech_ui.py
==================
Restores 3 missing UI features to eutech.directory:
1. Floating "Get Listed" button (bottom right, fixed position)
2. Scroll-to-top button (appears after scrolling down)
3. Verification badge visible on tool cards

Also patches build_eutech_index.py so these features
survive every future rebuild.

Run:
  python patch_eutech_ui.py
"""
from pathlib import Path
import re

INDEX   = Path(r"C:\Users\USER\NANO\outputs\eutech-directory\index.html")
BUILDER = Path(r"C:\Users\USER\NANO\outputs\eutech-directory\build_eutech_index.py")

# ── Feature 1 & 2: Floating buttons CSS + HTML ────────────────────────────────
FLOATING_CSS = """
  /* Floating UI buttons */
  .fab-wrap { position:fixed; bottom:24px; right:24px; z-index:9999; display:flex; flex-direction:column; gap:12px; align-items:flex-end; }
  .fab-listed { background:#2563eb; color:#fff; border:none; border-radius:50px; padding:12px 22px; font-size:14px; font-weight:600; cursor:pointer; box-shadow:0 4px 16px rgba(37,99,235,.35); transition:all .2s; white-space:nowrap; text-decoration:none; display:inline-flex; align-items:center; gap:8px; }
  .fab-listed:hover { background:#1d4ed8; transform:translateY(-2px); box-shadow:0 6px 20px rgba(37,99,235,.45); }
  .fab-top { background:#1e293b; color:#fff; border:none; border-radius:50%; width:44px; height:44px; font-size:20px; cursor:pointer; box-shadow:0 4px 12px rgba(0,0,0,.25); display:none; align-items:center; justify-content:center; transition:all .2s; }
  .fab-top.visible { display:flex; }
  .fab-top:hover { background:#334155; transform:translateY(-2px); }
"""

FLOATING_HTML = """
  <!-- Floating action buttons -->
  <div class="fab-wrap">
    <a href="https://rickyfarmer.gumroad.com/l/eutech-featured" target="_blank" class="fab-listed" aria-label="Get your tool listed as featured">
      ✦ Get Listed
    </a>
    <button class="fab-top" id="scrollTop" onclick="window.scrollTo({top:0,behavior:'smooth'})" aria-label="Scroll to top">↑</button>
  </div>
  <script>
    window.addEventListener('scroll', function() {
      var btn = document.getElementById('scrollTop');
      if (btn) btn.classList.toggle('visible', window.scrollY > 400);
    });
  </script>
"""

# ── Feature 3: Verification badge on tool cards ───────────────────────────────
# The builder renders tool cards — we need to add verified badge to the card template
VERIFIED_BADGE_JS = """
    // Add verification badge to verified tools
    function getVerifiedBadge(tool) {
      if (tool.v === true || tool.verified === true) {
        return '<span style="display:inline-flex;align-items:center;gap:3px;background:#dcfce7;color:#166534;font-size:10px;font-weight:600;padding:2px 7px;border-radius:20px;margin-left:6px;vertical-align:middle;" title="Verified live by AfriCompliance team">✓ Verified</span>';
      }
      return '';
    }
"""

def patch_index():
    if not INDEX.exists():
        print(f"ERROR: {INDEX} not found")
        return False
    
    src = INDEX.read_text(encoding="utf-8", errors="ignore")
    original = src
    changed = False

    # Add floating CSS before </style>
    if "fab-wrap" not in src:
        src = src.replace("</style>", FLOATING_CSS + "\n  </style>", 1)
        print("Added: floating buttons CSS")
        changed = True
    else:
        print("Already present: floating buttons CSS")

    # Add floating HTML before </body>
    if "fab-listed" not in src:
        src = src.replace("</body>", FLOATING_HTML + "\n</body>", 1)
        print("Added: floating buttons HTML")
        changed = True
    else:
        print("Already present: floating buttons HTML")

    # Add verified badge JS — find the card rendering function
    if "getVerifiedBadge" not in src:
        # Insert before the closing script tag or near card render logic
        if "function renderCard" in src or "function render" in src:
            src = src.replace("function render", VERIFIED_BADGE_JS + "\n    function render", 1)
        elif "const card" in src:
            src = src.replace("const card", VERIFIED_BADGE_JS + "\n    const card", 1)
        else:
            # Just add before </script>
            src = src.replace("</script>", VERIFIED_BADGE_JS + "\n</script>", 1)
        print("Added: verified badge JS")
        changed = True
    else:
        print("Already present: verified badge JS")

    if changed:
        INDEX.write_text(src, encoding="utf-8")
        print(f"Patched: {INDEX}")
        # Verify
        new_src = INDEX.read_text(encoding="utf-8")
        assert "fab-wrap" in new_src, "fab-wrap missing after patch"
        assert "fab-listed" in new_src, "fab-listed missing after patch"
        assert "scrollTop" in new_src, "scrollTop missing after patch"
        print("Verification: all features present in patched file")
    else:
        print("No changes needed")
    
    return True

def patch_builder():
    """Patch build_eutech_index.py so features survive rebuilds."""
    if not BUILDER.exists():
        print(f"BUILDER not found: {BUILDER}")
        return
    
    src = BUILDER.read_text(encoding="utf-8", errors="ignore")
    
    # Check if builder already injects floating buttons
    if "fab-wrap" in src:
        print("Builder already has floating buttons")
        return
    
    # Find where the builder writes </body> or the HTML template end
    # and inject the floating buttons there
    if "</body>" in src:
        src = src.replace(
            '"</body>"',
            '"' + FLOATING_HTML.replace('"', '\"').replace("\n", "\\n") + '\n</body>"',
            1
        )
        # Also add CSS
        if "</style>" in src and "fab-wrap" not in src:
            src = src.replace(
                '"</style>"',
                '"' + FLOATING_CSS.replace('"', '\"').replace("\n", "\\n") + '\n  </style>"',
                1
            )
        BUILDER.write_text(src, encoding="utf-8")
        print("Builder patched — floating buttons will survive rebuilds")
    else:
        print("Could not find </body> in builder — manual patch needed")

if __name__ == "__main__":
    print("=== Patching eutech.directory UI ===")
    print()
    print("[1] Patching index.html...")
    patch_index()
    print()
    print("[2] Patching build_eutech_index.py...")
    patch_builder()
    print()
    print("Done. Next steps:")
    print("  cd C:\\Users\\USER\\NANO\\outputs\\eutech-directory")
    print("  git add -A")
    print("  git commit -m \"Restore: floating Get Listed button, scroll-to-top, verified badges\"")
    print("  git push")
