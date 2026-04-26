"""
patch_eutech_index.py
=====================
Patches index.html in eutech-directory output folder:
1. Fixes Formspree ID (YOUR_FORM_ID -> xqewnpwl)
2. Adds "How to get listed" section with criteria
3. Adds criteria CSS styles
4. Updates submit section heading to be clearer

Run:
    python patch_eutech_index.py
"""

import re
from pathlib import Path

INDEX = Path(r"C:/Users/USER/NANO/outputs/eutech-directory/index.html")

def patch():
    print(f"Reading {INDEX}...")
    source = INDEX.read_text(encoding="utf-8-sig")
    original_len = len(source)
    changes = []

    # ── 1. Fix Formspree ID ────────────────────────────────────────────────
    old_action = "https://formspree.io/f/YOUR_FORM_ID"
    new_action = "https://formspree.io/f/xqewnpwl"
    if old_action in source:
        source = source.replace(old_action, new_action)
        changes.append("✓ Fixed Formspree form ID")
    elif new_action in source:
        changes.append("— Formspree ID already correct")
    else:
        changes.append("✗ Formspree action not found — check manually")

    # ── 2. Add criteria CSS ────────────────────────────────────────────────
    criteria_css = """
    /* ── Listing criteria ───────────────────────────────────────────────── */
    .listing-criteria {
      background: var(--surface);
      border-top: 1px solid var(--border);
      padding: 48px 24px;
      max-width: 800px;
      margin: 0 auto;
      text-align: center;
    }
    .listing-criteria h2 {
      font-size: 1.5rem;
      font-weight: 700;
      margin-bottom: 10px;
    }
    .criteria-intro {
      color: var(--muted);
      font-size: 0.95rem;
      margin-bottom: 28px;
      max-width: 540px;
      margin-left: auto;
      margin-right: auto;
    }
    .criteria-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
      margin-bottom: 24px;
      text-align: left;
    }
    @media (max-width: 600px) {
      .criteria-grid { grid-template-columns: 1fr; }
    }
    .criterion {
      display: flex;
      gap: 12px;
      align-items: flex-start;
      background: var(--bg);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 14px 16px;
    }
    .criterion-icon { font-size: 1.4rem; flex-shrink: 0; margin-top: 2px; }
    .criterion strong { display: block; font-size: 0.9rem; margin-bottom: 3px; }
    .criterion p { font-size: 0.82rem; color: var(--muted); line-height: 1.4; margin: 0; }
    .criteria-cta {
      font-size: 0.9rem;
      color: var(--accent);
      font-weight: 500;
    }
    """

    # Insert CSS before closing </style>
    if ".listing-criteria" not in source:
        source = source.replace("</style>", criteria_css + "\n    </style>", 1)
        changes.append("✓ Added listing criteria CSS")
    else:
        changes.append("— Criteria CSS already present")

    # ── 3. Add criteria section before submit-section div ──────────────────
    criteria_html = """
<!-- ── How to get listed ──────────────────────────────────────────────── -->
<div class="listing-criteria">
  <h2>How to get listed</h2>
  <p class="criteria-intro">eutech.directory lists EU-built and EU-hosted software. To be included, your tool must meet all criteria:</p>
  <div class="criteria-grid">
    <div class="criterion">
      <span class="criterion-icon">🇪🇺</span>
      <div>
        <strong>EU-built or EU-hosted</strong>
        <p>Company founded in the EU, or primary servers in EU data centres.</p>
      </div>
    </div>
    <div class="criterion">
      <span class="criterion-icon">🔒</span>
      <div>
        <strong>GDPR compliant by default</strong>
        <p>Data protection built into the architecture — not just a checkbox.</p>
      </div>
    </div>
    <div class="criterion">
      <span class="criterion-icon">☁️</span>
      <div>
        <strong>No US cloud dependencies</strong>
        <p>Data does not transit through or rest on AWS, GCP, or Azure US regions.</p>
      </div>
    </div>
    <div class="criterion">
      <span class="criterion-icon">✅</span>
      <div>
        <strong>Actively maintained</strong>
        <p>Live, usable, and updated within the last 12 months.</p>
      </div>
    </div>
  </div>
  <p class="criteria-cta">Meet all criteria? Submit below — we review within 24 hours.</p>
</div>
"""

    submit_marker = '<div class="submit-section">'
    if "How to get listed" not in source:
        if submit_marker in source:
            source = source.replace(submit_marker,
                                    criteria_html + "\n" + submit_marker, 1)
            changes.append("✓ Added 'How to get listed' section")
        else:
            changes.append("✗ submit-section div not found — check manually")
    else:
        changes.append("— 'How to get listed' already present")

    # ── 4. Update submit section heading ──────────────────────────────────
    old_heading = "<h2>Submit a tool</h2>"
    new_heading = "<h2>Submit your tool</h2>"
    if old_heading in source:
        source = source.replace(old_heading, new_heading, 1)
        changes.append("✓ Updated submit heading")

    # ── 5. Write back ──────────────────────────────────────────────────────
    INDEX.write_text(source, encoding="utf-8")
    new_len = len(source)

    print(f"\nResults:")
    for c in changes:
        print(f"  {c}")
    print(f"\nFile size: {original_len:,} → {new_len:,} bytes (+{new_len-original_len:,})")
    print(f"\nVerify form ID:")

    # Verify
    source_check = INDEX.read_text(encoding="utf-8")
    if "xqewnpwl" in source_check:
        print("  ✓ Formspree ID: xqewnpwl confirmed")
    if "How to get listed" in source_check:
        print("  ✓ Listing criteria section: present")
    if "criteria-grid" in source_check:
        print("  ✓ Criteria CSS: present")

    print(f"\nNext: git commit and push to deploy")

if __name__ == "__main__":
    patch()
