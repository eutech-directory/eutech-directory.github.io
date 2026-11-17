# Running eutech.directory

A one-page guide so anyone can run the site.

## How it works

- The site is static, hosted on **GitHub Pages**. The domain `eutech.directory` is registered at **Hostinger**, and its DNS points to GitHub Pages (see `CNAME`).
- Listings live in **`data/tools.json`**. Featured tools and Editor's picks are listed in **`data/highlights.json`** (chosen by the editors, not paid).
- **`build_site.py`** builds `index.html`, `mcp-servers/index.html`, every tool page, every category page and `sitemap.xml` from those files and `site_template.html`. Change the design in `site_template.html`, never in `index.html`.
- When anything in `data/`, `site_template.html` or `build_site.py` is pushed, **GitHub Actions rebuilds the pages automatically** (`.github/workflows/build.yml`).
- The "EU alternative to ..." pages in `alternatives/` are built by `patch_eutech_alternatives.py`; each company's country and the source checked are recorded in `alternatives/alternatives_data.json`.
- `build_eutech_index.py` is the old builder and is no longer used.

## Weekly routine (about 30 minutes)

1. Review new submissions (Formspree). Check each company's country on its own legal notice, terms or a company register. Reject anything that is not European software.
2. Add approved tools to the database, run `python export_tools_json.py`, then `python eutech_country_check.py check`, review `data/country_review.csv` and `python eutech_country_check.py apply --db`. New tools stay hidden until their country is confirmed.
3. Commit and push only the files in `data/`. GitHub rebuilds the site in a few minutes. Then run `git pull` so your copy has the rebuilt pages.
4. Once a month, rotate Featured and Editor's picks in `data/highlights.json`.
5. Check Cloudflare Web Analytics and Google Search Console weekly.

## Rules

- Never commit passwords, database addresses or API keys; they stay in environment variables on the PC.
- If paid placements are ever offered, label them clearly as "Sponsored".
- List a company only after checking its country on a primary source, and keep the source link.

## Accounts that go with the site

Hostinger (domain), GitHub (repository), Cloudflare Web Analytics, Formspree (submission form), Google Search Console. A buyer needs each one transferred or replaced.
