#!/usr/bin/env python3
"""Copy the main site's About page (about.html) into concept-v3 as about/index.html,
inside concept-v3's own header, mobile menu and footer.

Run from the repository root:  python3 concept-v3/src/make_about.py"""
import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SITE = os.path.join(ROOT, 'concept-v3', 'site')
main = open(os.path.join(ROOT, 'about.html'), encoding='utf-8').read()
tpl = open(os.path.join(SITE, 'states', 'index.html'), encoding='utf-8').read()   # a concept-v3 page one folder deep
R = '../'
EMAIL = 'contact.nigeriase4all@gmail.com'

# concept-v3 head with the main page's title and description
head = tpl[:tpl.index('</head>')]
head = re.sub(r'<title>[^<]*</title>', re.search(r'<title>[^<]*</title>', main).group(0), head)
desc = re.search(r'<meta name="description"[^>]*>', main).group(0)
head = re.sub(r'<meta name="description"[^>]*>', desc, head) if '<meta name="description"' in head else head.replace('</title>', '</title>\n    ' + desc, 1)
head = head.replace('family=Source+Serif+4:wght@600;700&family=Source+Sans+3:wght@400;500;600;700', 'family=Inter:wght@400;500;600;700')
head = re.sub(r'\s*<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/[^"]*">', '', head)

chrome_top = tpl[tpl.index('<body'):tpl.index('<main id="main">')]
chrome_top = re.sub(r'<body[^>]*>', '<body class="page-about">', chrome_top, count=1)
footer = tpl[tpl.index('<footer'):tpl.index('</footer>') + len('</footer>')]

# the main page's About content, with paths and links adjusted for concept-v3
body = main[main.index('<section class="phero'):main.index('</main>')]
band = main[main.index('<section class="support-band"'):main.index('<footer')] if '<section class="support-band"' in main else ''   # funding partners strip, outside <main> on the main site
body = body.replace('src="assets/', f'src="{R}assets/').replace('href="index.html"', f'href="{R}index.html"')
body = body.replace('href="power-sector.html#targets">See progress on the power sector page', 'href="https://apps.nigeriase4all.gov.ng/power-sector?grid_buffer=3" target="_blank" rel="noopener">See progress on the power sector webmap')
body = re.sub(r'(Find investment opportunities, case studies and market intelligence\.</p><a class="link" )href="#"', r'\1href="https://deepaccrete.github.io/NESP-OSIP-HTML/homepage.html"', body)
body = body.replace('mailto:[contact@rea.gov.ng]', f'mailto:{EMAIL}').replace('[contact@rea.gov.ng]', EMAIL)

page = (head.rstrip() + '\n</head>\n' + chrome_top + '<main id="main">\n' + body + '</main>\n' + band.replace('src="assets/', f'src="{R}assets/') + footer + '\n'
        f'<script>window.PAGE={{"root": "{R}", "kind": "about"}};</script>\n<script src="{R}assets/js/v9.js"></script>\n</body>\n</html>\n')
os.makedirs(os.path.join(SITE, 'about'), exist_ok=True)
out = os.path.join(SITE, 'about', 'index.html')
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from clean_footer import fix as _cf; page = _cf(page)
open(out, 'w', encoding='utf-8').write(page)
print('wrote', out, len(page))
