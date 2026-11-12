# patch_eutech_alternatives.py
# Rewrites the 20 "EU alternative to ..." pages from a checked list of tools.
# - Each tool: company name, country and the page where that was checked.
# - Companies outside the EU (UK, Switzerland, Norway) are clearly marked.
# - No automatic "Featured" badge. No uptime or "no US cloud" claims.
# Run from the repo root:  python patch_eutech_alternatives.py
import html, json, os, re, sys

CHECKED = "12 November 2026"
CHECKED_ISO = "2026-11-12"
SITE = "https://eutech.directory"

EU = {"AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR", "HU", "IE", "IT",
      "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK", "SI", "ES", "SE"}
COUNTRY = {"AT": "Austria", "BE": "Belgium", "CZ": "Czechia", "DE": "Germany", "EE": "Estonia",
           "ES": "Spain", "FR": "France", "LT": "Lithuania", "LU": "Luxembourg", "LV": "Latvia",
           "NL": "Netherlands", "PL": "Poland", "SI": "Slovenia", "UK": "United Kingdom",
           "CH": "Switzerland", "NO": "Norway"}
OUTSIDE_NOTE = {
    "UK": "Outside the EU. UK GDPR applies; the EU recognises UK data protection as adequate.",
    "CH": "Outside the EU. Swiss data protection law applies; the EU recognises it as adequate.",
    "NO": "Outside the EU but in the EEA, so the GDPR applies in full.",
}


def flag(cc):
    cc = "GB" if cc == "UK" else cc
    return "".join(chr(0x1F1E6 + ord(c) - 65) for c in cc)


# ── Tools: name, website, country, legal entity + city, what it does, source checked, note ──
T = {
    "plausible": ("Plausible Analytics", "https://plausible.io", "EE", "Plausible Insights OÜ, Tartu",
                  "Lightweight, cookie-free website analytics. Open source; can be self-hosted.",
                  "https://plausible.io/privacy", ""),
    "simpleanalytics": ("Simple Analytics", "https://www.simpleanalytics.com", "NL", "Simple Analytics B.V., Amsterdam",
                        "Privacy-first website analytics with no cookies and no personal data collected.",
                        "https://www.simpleanalytics.com/about", ""),
    "pirsch": ("Pirsch", "https://pirsch.io", "DE", "Emvi Software GmbH",
               "Cookie-free, server-side website analytics.", "https://pirsch.io/about-us", ""),
    "piwikpro": ("Piwik PRO", "https://piwik.pro", "PL", "Piwik PRO SA, Wrocław",
                 "Analytics suite with tag manager and consent manager, aimed at larger organisations.",
                 "https://piwik.pro/privacy-policy/", ""),
    "element": ("Element", "https://element.io", "UK", "Element Creations Ltd, London (Companies House 10873661)",
                "Team chat and calls on the open Matrix protocol. Hosted or self-hosted, end-to-end encrypted.",
                "https://find-and-update.company-information.service.gov.uk/company/10873661", ""),
    "stackfield": ("Stackfield", "https://www.stackfield.com", "DE", "Stackfield GmbH, Munich",
                   "All-in-one workspace: chat, tasks, video calls, documents and calendar.",
                   "https://www.stackfield.com/contact", ""),
    "threema": ("Threema Work", "https://threema.ch/en/work", "CH", "Threema AG, Pfäffikon SZ",
                "Encrypted business messenger with group chats and calls.",
                "https://threema.com/en/impressum", ""),
    "nuclino": ("Nuclino", "https://www.nuclino.com", "DE", "Nuclino GmbH, Grünwald",
                "Team wiki and docs with linked pages, boards and graph view.",
                "https://www.nuclino.com/terms", ""),
    "anytype": ("Anytype", "https://anytype.io", "CH", "Any Association, Zug",
                "Local-first notes, docs and databases with end-to-end encrypted sync.",
                "https://business.anytype.io/tos", "EU representative: Anylab GmbH, Berlin."),
    "nextcloud": ("Nextcloud", "https://nextcloud.com", "DE", "Nextcloud GmbH, Stuttgart",
                  "Open-source file sync and sharing with office, calendar and chat. Self-hosted or via a provider.",
                  "https://nextcloud.com/de/impressum/", ""),
    "codeberg": ("Codeberg", "https://codeberg.org", "DE", "Codeberg e.V. (non-profit association), Berlin",
                 "Non-profit Git hosting for open-source projects, running Forgejo.",
                 "https://docs.codeberg.org/getting-started/what-is-codeberg/",
                 "Meant mainly for free and open-source projects. For private company code, self-host Forgejo."),
    "youtrack": ("YouTrack", "https://www.jetbrains.com/youtrack/", "CZ", "JetBrains s.r.o., Prague",
                 "Issue tracker and agile boards, with a knowledge base.",
                 "https://www.jetbrains.com/youtrack/buy/license.html", ""),
    "openproject": ("OpenProject", "https://www.openproject.org", "DE", "OpenProject GmbH, Berlin",
                    "Open-source project management: work packages, Gantt charts, agile boards.",
                    "https://www.openproject.org/legal/imprint/", ""),
    "taiga": ("Taiga", "https://taiga.io", "ES", "Kaleidos group, Spain",
              "Open-source agile project management with Scrum and Kanban boards.",
              "https://taiga.io/privacy-policy", ""),
    "meistertask": ("MeisterTask", "https://www.meistertask.com", "DE", "MeisterLabs GmbH, Vaterstetten (Munich area)",
                    "Kanban-style task and project management for teams.",
                    "https://search.lei-registrar.com/8945004PCX5QF4Y9O610", ""),
    "penpot": ("Penpot", "https://penpot.app", "ES", "Kaleidos Subsidiary S.L., Madrid",
               "Open-source design and prototyping tool. Runs in the browser; can be self-hosted.",
               "https://penpot.app/terms", ""),
    "alfaview": ("alfaview", "https://alfaview.com", "DE", "alfaview gmbh, Karlsruhe",
                 "Video conferencing for meetings, teaching and webinars.",
                 "https://alfaview.com/en/terms/", ""),
    "eyeson": ("eyeson", "https://www.eyeson.com", "AT", "eyeson GmbH, Graz",
               "Video meeting platform and video API.", "https://www.eyeson.com/terms-of-service", ""),
    "brevo": ("Brevo", "https://www.brevo.com", "DE", "Brevo GmbH, Berlin (part of the French Brevo group)",
              "Email marketing, transactional email, SMS and a simple CRM.",
              "https://www.brevo.com/de/legal/impressum/", ""),
    "mailerlite": ("MailerLite", "https://www.mailerlite.com", "LT", "MailerLite UAB, Vilnius",
                   "Email marketing with newsletters, automations and landing pages.",
                   "https://www.emis.cn/php/company-profile/LT/Mailerlite_UAB_en_8380920.html", ""),
    "cleverreach": ("CleverReach", "https://www.cleverreach.com", "DE", "CleverReach GmbH & Co. KG, Rastede",
                    "Email marketing and newsletter software.",
                    "https://datarequests.org/company/cleverreach", ""),
    "mailjet": ("Mailjet", "https://www.mailjet.com", "DE", "Mailjet GmbH, Berlin (owned by Sinch, Sweden)",
                "Email marketing and transactional email API.", "https://www.mailjet.com/impressum/", ""),
    "scalewaytem": ("Scaleway Transactional Email", "https://www.scaleway.com/en/transactional-email-tem/", "FR",
                    "Scaleway SAS, Paris (RCS Paris 433 115 904)",
                    "Transactional email sending (API and SMTP) from a European cloud.",
                    "https://www.scaleway.com/en/legal-notice/", ""),
    "internxt": ("Internxt", "https://internxt.com", "ES", "Internxt Universal Technologies SL, Valencia",
                 "Encrypted cloud storage. Open source.", "https://help.internxt.com", ""),
    "filen": ("Filen", "https://filen.io", "DE", "Filen Cloud Dienste UG",
              "End-to-end encrypted cloud storage.", "https://filen.io/about", ""),
    "koofr": ("Koofr", "https://koofr.eu", "SI", "Koofr d.o.o., Ljubljana",
              "Cloud storage that can also connect your other cloud accounts.", "https://www.startup.si/en-us/startup-map/startups-scaleups/koofr", ""),
    "pcloud": ("pCloud", "https://www.pcloud.com", "CH", "pCloud International AG, Baar",
               "Cloud storage with optional client-side encryption and EU data region.",
               "https://help.pcloud.com/article/terms-of-service", "Choose the EU data region when you sign up."),
    "tresorit": ("Tresorit", "https://tresorit.com", "CH", "Tresorit AG, Zurich",
                 "End-to-end encrypted file sharing and storage for business.",
                 "https://tresorit.com/terms-of-use", ""),
    "hetzner": ("Hetzner", "https://www.hetzner.com", "DE", "Hetzner Online GmbH, Gunzenhausen (HRB 6089)",
                "Cloud servers, dedicated servers, storage and load balancers.",
                "https://www.hetzner.com/legal/legal-notice/",
                "Has data centres in Germany and Finland, and also in the US and Singapore. Pick an EU location."),
    "ovhcloud": ("OVHcloud", "https://www.ovhcloud.com", "FR", "OVH SAS, Roubaix (RCS Lille 424 761 419)",
                 "Public cloud, bare-metal servers, storage and managed Kubernetes.",
                 "https://www.ovhcloud.com/en-gb/terms-and-conditions/", "Pick an EU region; it also runs data centres outside Europe."),
    "scaleway": ("Scaleway", "https://www.scaleway.com", "FR", "Scaleway SAS, Paris (RCS Paris 433 115 904)",
                 "Cloud instances, GPUs, object storage, managed databases and Kubernetes.",
                 "https://www.scaleway.com/en/legal-notice/", ""),
    "ionos": ("IONOS Cloud", "https://cloud.ionos.com", "DE", "IONOS SE, Montabaur (HRB 24498)",
              "Compute, storage, managed Kubernetes and hosting.", "https://www.ionos.de/impressum", ""),
    "teamleader": ("Teamleader", "https://www.teamleader.eu", "BE", "Teamleader NV, Ghent",
                   "CRM with quotes, invoicing and projects for small businesses.",
                   "https://www.teamleader.eu/legal/terms-of-service-teamleader-focus", ""),
    "superoffice": ("SuperOffice CRM", "https://www.superoffice.com", "NO", "SuperOffice AS, Oslo",
                    "CRM for sales, marketing and customer service.",
                    "https://www.superoffice.com/trust-center/transparency/", ""),
    "odoo": ("Odoo", "https://www.odoo.com", "BE", "Odoo SA, Ramillies",
             "Open-source business apps: CRM, sales, accounting, inventory and more.",
             "https://companyweb.be/en/0477472701/odoo", ""),
    "checkmk": ("Checkmk", "https://checkmk.com", "DE", "Checkmk GmbH, Munich (HRB 165902)",
                "Infrastructure and application monitoring. Open-source edition available.",
                "https://checkmk.com/imprint", ""),
    "zabbix": ("Zabbix", "https://www.zabbix.com", "LV", "SIA Zabbix, Riga (reg. 40003738045)",
               "Open-source monitoring for networks, servers, cloud and applications.",
               "https://www.zabbix.com/privacy_policy", ""),
    "passbolt": ("Passbolt", "https://www.passbolt.com", "LU", "Passbolt SA, Belvaux",
                 "Open-source password manager built for teams. Cloud or self-hosted.",
                 "https://www.passbolt.com/terms/cloud/customer", ""),
    "psono": ("Psono", "https://psono.com", "DE", "esaqa GmbH, Vorra (HRB 37978)",
              "Open-source password manager for teams, self-hosted or cloud.",
              "https://psono.com/da/legal-notice", ""),
    "protonpass": ("Proton Pass", "https://proton.me/pass", "CH", "Proton AG, Plan-les-Ouates (Geneva)",
                   "End-to-end encrypted password manager with email aliases.",
                   "https://moneyhouse.ch/en/company/proton-ag-4537282131", ""),
    "sage": ("Sage Accounting", "https://www.sage.com", "UK", "The Sage Group plc, Newcastle upon Tyne (02231246)",
             "Cloud accounting and payroll for small businesses.",
             "https://find-and-update.company-information.service.gov.uk/company/02231246",
             "Product versions differ by country."),
    "freeagent": ("FreeAgent", "https://www.freeagent.com", "UK", "FreeAgent Central Ltd, Edinburgh (SC316774)",
                  "Accounting for freelancers and small businesses, built for UK tax.",
                  "https://find-and-update.company-information.service.gov.uk/company/SC316774", "UK only."),
    "exact": ("Exact Online", "https://www.exact.com", "NL", "Exact Group B.V., Delft (KvK 27225823)",
              "Cloud accounting and ERP for small and mid-sized businesses.",
              "https://files.exact.com/static/web/pdf/Privacy-Policy-for-Exact-Services-EN.pdf",
              "Available in selected countries (for example NL, BE, DE, UK, FR, ES)."),
    "pennylane": ("Pennylane", "https://www.pennylane.com", "FR", "Pennylane SAS, Paris (RCS 880 265 921)",
                  "Accounting and finance platform shared by businesses and their accountants.",
                  "https://www.pennylane.com/fr/legal/mentions-legales", "Mainly for French businesses."),
    "storyblok": ("Storyblok", "https://www.storyblok.com", "AT", "Storyblok GmbH, Linz (FN 479743f)",
                  "Headless CMS with a visual editor.",
                  "https://www.storyblok.com/legal/general-terms-and-conditions-31082023", ""),
    "kontent": ("Kontent.ai", "https://kontent.ai", "CZ", "Kontent CZ s.r.o., Brno",
                "Headless CMS for teams and enterprises.",
                "https://europeanpurpose.com/tool/kontent-ai",
                "Its terms allow a US group company to be the contracting party. Check who signs your contract."),
}
for k, v in T.items():
    assert v[2] in COUNTRY, k

# ── Pages ──
P = [
    ("google-analytics", "Google Analytics", "web analytics",
     ["plausible", "simpleanalytics", "pirsch", "piwikpro"],
     "Most of these work without cookies, so you may not need a cookie banner for analytics. Check that with your own legal advice."),
    ("slack", "Slack", "team chat", ["element", "stackfield", "threema"],
     "Element is closest to Slack for channels and integrations. Stackfield adds tasks and documents in one place."),
    ("notion", "Notion", "docs and wiki", ["nuclino", "anytype", "nextcloud"],
     "Nuclino is the closest for a team wiki. Anytype keeps your data on your own devices first."),
    ("github", "GitHub", "code hosting", ["codeberg"],
     "Only one hosted option passed our checks. Many teams self-host Forgejo (the software behind Codeberg) on an EU server instead."),
    ("jira", "Jira", "issue tracking", ["youtrack", "openproject", "taiga", "stackfield"],
     "YouTrack is the closest to Jira for software teams. OpenProject and Taiga are open source and can be self-hosted."),
    ("zoom", "Zoom", "video meetings", ["alfaview", "eyeson", "element"],
     "Check how many participants each plan allows and whether webinars are included."),
    ("mailchimp", "Mailchimp", "email marketing", ["brevo", "mailerlite", "cleverreach", "mailjet"],
     "All four import contact lists from Mailchimp as a CSV file."),
    ("dropbox", "Dropbox", "file storage and sharing", ["internxt", "filen", "koofr", "pcloud", "tresorit", "nextcloud"],
     "Tresorit, Filen and Internxt encrypt files end to end. For pCloud, choose the EU data region."),
    ("google-drive", "Google Drive", "cloud storage", ["nextcloud", "internxt", "filen", "koofr", "pcloud", "tresorit"],
     "Nextcloud adds online office documents, which is the closest match to Google Drive with Docs and Sheets."),
    ("aws", "AWS", "cloud infrastructure", ["hetzner", "ovhcloud", "scaleway", "ionos"],
     "None of these offer every AWS service. Compare the specific services you use, and pick an EU region."),
    ("google-cloud", "Google Cloud", "cloud infrastructure", ["scaleway", "ovhcloud", "hetzner", "ionos"],
     "None of these offer every Google Cloud service. Compare the specific services you use, and pick an EU region."),
    ("hubspot", "HubSpot", "CRM and marketing", ["brevo", "teamleader", "odoo", "superoffice"],
     "Brevo is the closest for email marketing plus CRM. Teamleader and Odoo add quotes and invoicing."),
    ("salesforce", "Salesforce", "CRM", ["superoffice", "odoo", "teamleader"],
     "SuperOffice is closest for larger sales teams. Odoo covers CRM plus the rest of the business."),
    ("figma", "Figma", "design and prototyping", ["penpot"],
     "Penpot is the only close match that passed our checks. It can import Figma files through a plugin; check how well your files convert."),
    ("asana", "Asana", "task and project management", ["meistertask", "stackfield", "openproject", "taiga"],
     "MeisterTask is the closest for simple task boards. OpenProject suits bigger projects with timelines."),
    ("datadog", "Datadog", "monitoring", ["checkmk", "zabbix"],
     "Both are mature monitoring tools with open-source editions. Neither copies every Datadog feature."),
    ("1password", "1Password", "password management", ["passbolt", "psono", "protonpass"],
     "Passbolt and Psono are built for teams and can be self-hosted. Proton Pass is simplest for individuals and small teams."),
    ("sendgrid", "SendGrid", "transactional email", ["brevo", "mailjet", "scalewaytem"],
     "Check sending limits and dedicated IP options on each plan."),
    ("quickbooks", "QuickBooks", "accounting", ["sage", "exact", "pennylane", "freeagent"],
     "Accounting software must follow your country's tax rules. Check that the tool supports your country before you switch."),
    ("contentful", "Contentful", "headless CMS", ["storyblok", "kontent"],
     "Both are hosted headless CMSs with APIs similar to Contentful's."),
]
assert len(P) == 20

CSS = """*{box-sizing:border-box;margin:0;padding:0}
body{font-family:system-ui,-apple-system,sans-serif;background:#0d1117;color:#e6edf3;line-height:1.6}
.wrap{max-width:960px;margin:0 auto;padding:24px 16px}
nav{display:flex;justify-content:space-between;align-items:center;padding:16px 0;border-bottom:1px solid #21262d;margin-bottom:28px}
.logo{font-size:20px;font-weight:700;color:#fff;text-decoration:none}.logo b{color:#00bcd4}
.bc{font-size:13px;color:#8b949e;margin-bottom:16px}.bc a{color:#00bcd4;text-decoration:none}
h1{font-size:28px;font-weight:700;color:#fff;margin-bottom:8px;line-height:1.25}
.lead{font-size:16px;color:#9da7b3;margin-bottom:12px}
.tip{background:#0f2a33;border:1px solid #00bcd444;border-radius:8px;padding:12px 16px;font-size:14px;color:#cfe9ee;margin:16px 0 8px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:14px;margin:20px 0}
.card{background:#161b22;border:1px solid #21262d;border-radius:10px;padding:16px;display:flex;flex-direction:column}
.card h2{font-size:16px;font-weight:600;margin-bottom:6px}
.card h2 a{color:#e6edf3;text-decoration:none}.card h2 a:hover{color:#00bcd4}
.where{font-size:13px;color:#e6edf3;margin-bottom:2px}
.ent{font-size:12px;color:#8b949e;margin-bottom:8px}
.out{display:inline-block;background:#3b2f0b;color:#fcd34d;border:1px solid #a16207;font-size:11px;padding:2px 8px;border-radius:4px;margin-bottom:8px}
.desc{font-size:13px;color:#b1bac4;line-height:1.5;margin-bottom:8px}
.note{font-size:12px;color:#fcd34d;margin-bottom:8px}
.src{font-size:11px;color:#8b949e;margin-top:auto;margin-bottom:8px}.src a{color:#8b949e}
.vl{color:#00bcd4;font-size:13px;font-weight:500;text-decoration:none}.vl:hover{text-decoration:underline}
.box{background:#161b22;border:1px solid #21262d;border-radius:10px;padding:20px;margin:24px 0}
.box h2{font-size:18px;font-weight:600;color:#fff;margin-bottom:12px}
.box ul{padding-left:20px}.box li{font-size:14px;color:#b1bac4;margin-bottom:8px}.box li strong{color:#e6edf3}
.faq{margin:24px 0}.faq h2{font-size:20px;font-weight:600;color:#fff;margin-bottom:14px}
.fq{border-bottom:1px solid #21262d;padding:12px 0}
.fq-q{font-size:15px;font-weight:500;color:#e6edf3;margin-bottom:6px}
.fq-a{font-size:14px;color:#b1bac4}
.cta{background:linear-gradient(135deg,#001a2e,#002d4a);border:1px solid #00bcd433;border-radius:10px;padding:20px;display:flex;justify-content:space-between;align-items:center;gap:16px;flex-wrap:wrap;margin:24px 0}
.cta h3{font-size:16px;font-weight:600;color:#fff;margin-bottom:3px}.cta p{font-size:13px;color:#9da7b3}
.cta-btn{background:#00bcd4;color:#000;font-size:13px;font-weight:700;padding:10px 20px;border-radius:8px;text-decoration:none;white-space:nowrap}
.more{font-size:14px;color:#9da7b3;margin:8px 0 0}.more a{color:#00bcd4;text-decoration:none;margin-right:12px;display:inline-block}
footer{border-top:1px solid #21262d;padding:20px 0;font-size:13px;color:#8b949e;display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px}
footer a{color:#00bcd4;text-decoration:none}"""

HEAD_EXTRA = ('<!-- eutech favicon --><link rel="icon" href="/favicon.ico" sizes="32x32"><link rel="icon" href="/favicon.svg" '
              'type="image/svg+xml"><link rel="apple-touch-icon" href="/apple-touch-icon.png"><link rel="manifest" '
              'href="/site.webmanifest"><meta name="theme-color" content="#0B3D91">')
CF = ("<!-- Cloudflare Web Analytics --><script type='module' src='https://static.cloudflareinsights.com/beacon.min.js' "
      "data-cf-beacon='{\"token\": \"c87f4229eb7e44a19c5e152941ca0275\"}'></script><!-- End Cloudflare Web Analytics -->")

e = html.escape


def where_text(cc):
    return flag(cc) + " " + COUNTRY[cc] + ("" if cc in EU else "")


def card(k):
    name, url, cc, ent, desc, src, note = T[k]
    out = "" if cc in EU else '<span class="out">' + e(OUTSIDE_NOTE[cc]) + "</span>"
    return ('<div class="card"><h2><a href="' + e(url) + '" rel="noopener" target="_blank">' + e(name) + "</a></h2>"
            '<div class="where">' + where_text(cc) + "</div>"
            '<div class="ent">' + e(ent) + "</div>" + out +
            '<p class="desc">' + e(desc) + "</p>" +
            ('<p class="note">' + e(note) + "</p>" if note else "") +
            '<p class="src">Company checked ' + CHECKED + ': <a href="' + e(src) + '" rel="noopener nofollow" target="_blank">source</a></p>'
            '<a href="' + e(url) + '" class="vl" rel="noopener" target="_blank">Visit ' + e(name) + " →</a></div>")


def page(slug, prod, kind, keys, tip):
    names = [T[k][0] for k in keys]
    n = len(keys)
    outside = [T[k][0] + " (" + COUNTRY[T[k][2]] + ")" for k in keys if T[k][2] not in EU]
    canon = SITE + "/alternatives/eu-alternative-to-" + slug + "/"
    title = "European alternatives to " + prod + " (checked " + CHECKED.split(" ", 1)[1] + ")"
    if n == 1:
        lead = names[0] + " is a European " + kind + " tool that can replace " + prod + "."
        best = names[0]
    else:
        lead = str(n) + " " + kind + " tools from European companies that can replace " + prod + "."
        best = ", ".join(names[:-1]) + " and " + names[-1]
    meta = (lead + " Each company's country checked against its own legal page or company register.")[:300]
    q_best = "What is a good European alternative to " + prod + "?"
    a_best = ("Options from European companies include " + best + ". " + tip)
    q_where = "Where are these companies based?"
    a_where = "; ".join(T[k][0] + ": " + COUNTRY[T[k][2]] for k in keys) + "."
    if outside:
        a_where += " " + (outside[0] if len(outside) == 1 else ", ".join(outside[:-1]) + " and " + outside[-1]) + (" is" if len(outside) == 1 else " are") + " outside the EU and marked on this page."
    q_gdpr = "Does a European company mean my data stays in Europe?"
    a_gdpr = ("Not automatically. A company based in Europe must follow European data protection law, but it may still host data "
              "in other regions or use other providers. Check where your data is stored and the provider's list of sub-processors before you switch.")
    faq = [(q_best, a_best), (q_where, a_where), (q_gdpr, a_gdpr)]
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "ItemList", "name": "European alternatives to " + prod, "numberOfItems": n,
         "itemListElement": [{"@type": "ListItem", "position": i + 1, "item": {
             "@type": "SoftwareApplication", "name": T[k][0], "url": T[k][1], "applicationCategory": "BusinessApplication",
             "description": T[k][4]}} for i, k in enumerate(keys)]},
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                                            for q, a in faq]},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "European alternatives to " + prod}]}]}
    others = "".join('<a href="/alternatives/eu-alternative-to-' + s + '/">' + e(p) + "</a>"
                     for s, p, *_ in P if s != slug)
    return ("<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n<meta charset=\"UTF-8\"/><meta name=\"viewport\" content=\"width=device-width,initial-scale=1.0\"/>\n"
            "<title>" + e(title) + " — eutech.directory</title>\n"
            '<meta name="description" content="' + e(meta) + '"/>\n'
            '<link rel="canonical" href="' + canon + '"/>\n'
            '<meta property="og:title" content="' + e(title) + '"/>\n'
            '<meta property="og:description" content="' + e(meta) + '"/>\n'
            '<meta property="og:url" content="' + canon + '"/>\n<meta property="og:type" content="website"/>\n'
            '<script type="application/ld+json">\n' + json.dumps(ld, ensure_ascii=False).replace("</", "<\\/") + "\n</script>\n"
            "<style>\n" + CSS + "\n</style>\n" + HEAD_EXTRA + "\n</head>\n<body><div class=\"wrap\">\n"
            '<nav><a href="/" class="logo">eutech<b>.</b>directory</a><a href="/" style="font-size:13px;color:#00bcd4;text-decoration:none">← All tools</a></nav>\n'
            '<div class="bc"><a href="/">Home</a> › <a href="/#alternatives">Alternatives</a> › ' + e(prod) + "</div>\n"
            "<h1>European alternatives to " + e(prod) + "</h1>\n"
            '<p class="lead">' + e(lead) + " Companies are based in the EU, the UK, the EEA or Switzerland; any company outside the EU is marked.</p>\n"
            '<p class="tip">' + e(tip) + "</p>\n"
            '<div class="grid">' + "".join(card(k) for k in keys) + "</div>\n"
            '<div class="box"><h2>How we checked this list</h2><ul>\n'
            "<li><strong>Same job as " + e(prod) + ".</strong> Every tool here does " + e(kind) + ". Tools that only share a category are left out.</li>\n"
            "<li><strong>Company location.</strong> We checked each company's country on its own legal notice, terms or a public company register on " + CHECKED + ". The source is linked on each card.</li>\n"
            "<li><strong>No paid ranking.</strong> No tool paid to appear on this page or for its position.</li>\n"
            "<li><strong>Check before you switch.</strong> Prices, features, data locations and ownership change. Confirm them with the provider.</li>\n"
            "</ul></div>\n"
            '<div class="faq"><h2>Frequently asked questions</h2>\n' +
            "".join('<div class="fq"><p class="fq-q">' + e(q) + '</p><p class="fq-a">' + e(a) + "</p></div>\n" for q, a in faq) +
            "</div>\n"
            '<div class="cta"><div><h3>Know a European tool we missed?</h3><p>Send it in. We check the company before listing it.</p></div>'
            '<a href="/#submit" class="cta-btn">Submit a tool →</a></div>\n'
            '<p class="more">More alternatives: ' + others + "</p>\n"
            "<footer><span>eutech.directory — European software · Page checked " + CHECKED + "</span>"
            '<div style="display:flex;gap:16px"><a href="/">Browse all</a><a href="/#submit">Submit tool</a>'
            '<a href="https://legis-link.com/app">Legis-Link</a></div></footer>\n'
            "</div>" + CF + "\n</body></html>\n")


def main():
    root = os.getcwd()
    if not os.path.isdir(os.path.join(root, "alternatives")) or not os.path.isfile(os.path.join(root, "CNAME")):
        sys.exit("Run this from the eutech-directory repo folder (it must contain CNAME and alternatives/).")
    changed = []
    for slug, prod, kind, keys, tip in P:
        d = os.path.join(root, "alternatives", "eu-alternative-to-" + slug)
        os.makedirs(d, exist_ok=True)
        f = os.path.join(d, "index.html")
        new = page(slug, prod, kind, keys, tip)
        old = open(f, encoding="utf-8").read() if os.path.exists(f) else ""
        if old != new:
            with open(f, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(new)
            changed.append(f)
    # data file for future updates
    data = {"checked": CHECKED_ISO, "tools": {k: dict(zip(["name", "url", "country", "entity", "description", "source", "note"], v))
                                             for k, v in T.items()},
            "pages": [{"slug": s, "product": p, "kind": kd, "tools": ks, "tip": tp} for s, p, kd, ks, tp in P]}
    jf = os.path.join(root, "alternatives", "alternatives_data.json")
    js = json.dumps(data, ensure_ascii=False, indent=1) + "\n"
    if not os.path.exists(jf) or open(jf, encoding="utf-8").read() != js:
        with open(jf, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(js)
        changed.append(jf)
    # sitemap: refresh lastmod for these pages
    sm = os.path.join(root, "sitemap.xml")
    if os.path.exists(sm):
        s = open(sm, encoding="utf-8").read()
        s2 = re.sub(r"(<loc>[^<]*/alternatives/eu-alternative-to-[a-z0-9-]+/</loc>\s*<lastmod>)[0-9-]+(</lastmod>)",
                    r"\g<1>" + CHECKED_ISO + r"\g<2>", s)
        if s2 != s:
            with open(sm, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(s2)
            changed.append(sm)
    print("Updated", len(changed), "files")
    for c in changed:
        print("  ", os.path.relpath(c, root))


if __name__ == "__main__":
    main()
