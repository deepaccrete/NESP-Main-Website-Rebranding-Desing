# -*- coding: utf-8 -*-
"""Footer/link clean-up for the v3 site (Nov 2026): drop the World Bank and compare site-finder links,
the duplicate "Site-finder" link, Accreditation and Data health. Safe to run repeatedly.
Run: python3 concept-v3/src/clean_footer.py"""
import os, re
PATS = [
    r'<a href="[^"]*for/developers/world-bank/index\.html">Site finder \(World Bank DRE data\)</a>',
    r'<a href="[^"]*for/developers/compare/index\.html">Compare the site finders</a>',
    r'<a href="[^"]*for/developers/index\.html">Site-finder</a>',
    r'<a href="[^"]*#finder">Site-finder</a>',
    r'<a href="https://nigeriase4all\.gov\.ng/accreditation">Accreditation</a>',
    r'<a href="[^"]*data-health/index\.html">Data health</a>',
    r' · <a class="a-go" href="[^"]*data-health/index\.html">Data health</a>',
]
def fix(s):
    for p in PATS[::-1]: s = re.sub(p, "", s)
    # homepage card that pointed to the data-health page: point it at data downloads instead
    s = s.replace('<a class="a-usp " href="data-health/index.html">', '<a class="a-usp " href="index.html#data">')
    s = s.replace(", with a public data-health check that reports duplicates, missing licences and broken links.", ", with notes on known gaps in each dataset.")
    return s
if __name__ == "__main__":
    HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
    dirs = [os.path.join(ROOT, "site"), os.path.join(os.path.dirname(ROOT), "_backup", "states-before-redesign")]
    n = 0
    for d in dirs:
        for r, _, fs in os.walk(d):
            for f in fs:
                if f.endswith(".html"):
                    p = os.path.join(r, f); s = open(p, encoding="utf-8").read(); t = fix(s)
                    if t != s: open(p, "w", encoding="utf-8").write(t); n += 1
    print("cleaned", n, "files")
