#!/usr/bin/env python3
"""Put the Electrification Explorer (concept-explorer/index.html) into concept-v3 as the Site finder,
inside concept-v3's own header, mobile menu and footer.

Run from the repository root:  python3 concept-v3/src/make_site_finder.py
Writes concept-v3/site/for/developers/index.html (the address every "Site finder" link uses).
The first run keeps the original page as for/developers/site-finder-original.html."""
import os, re, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EXP = os.path.join(ROOT, 'concept-explorer', 'index.html')
SITE = os.path.join(ROOT, 'concept-v3', 'site')
DEST = os.path.join(SITE, 'for', 'developers', 'index.html')
ORIG = os.path.join(SITE, 'for', 'developers', 'site-finder-original.html')

if not os.path.exists(ORIG):
    shutil.copyfile(DEST, ORIG)
orig = open(ORIG, encoding='utf-8').read()
exp = open(EXP, encoding='utf-8').read()

# ---------- pieces of the concept-v3 page ----------
head = orig[:orig.index('</head>')]
head = re.sub(r'<title>[^<]*</title>', '<title>Site finder | Nigeria Electrification Atlas</title>', head)
head = head.replace('family=Source+Serif+4:wght@600;700&family=Source+Sans+3:wght@400;500;600;700', 'family=Inter:wght@400;500;600;700')
head = re.sub(r'\s*<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/[^"]*">', '', head)
head += '\n    <link href="https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.css" rel="stylesheet">'
chrome_top = orig[orig.index('<body'):orig.index('<main id="main">')]
footer = orig[orig.index('<footer'):orig.index('</footer>') + len('</footer>')]
footer = re.sub(r'href="((?:\.\./)*)index\.html#finder"', r'href="\1for/developers/index.html"', footer)
root = '../../'

# ---------- pieces of the explorer ----------
css = exp[exp.index('<style>') + 7:exp.index('</style>')]
body = exp[exp.index('<body>') + 6:exp.index('<script src="https://unpkg.com/maplibre-gl')]
app_js = exp[exp.index('<script>\n(() => {'):exp.rindex('</script>') + 9]

# drop the explorer's own header (concept-v3's header replaces it)
body = re.sub(r'<header class="hdr">.*?</header>', '', body, flags=re.S)
body = body.replace('<main class="app" id="app">', '<div class="app" id="xp">').replace('</main>\n<div class="toast" id="toast" role="status"></div>', '<div class="toast" id="toast" role="status"></div>\n</div>')
# shortlist button moves onto the map toolbar
body = body.replace('<div class="mgrp">', '<div class="mgrp">\n        <button class="mbtn" type="button" id="slBtn" title="Shortlist"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 3h12v18l-6-4-6 4z"/></svg><span>Shortlist</span><b class="sl-n" id="slN">0</b></button>', 1)
app_js = app_js.replace("document.querySelector('.brand .mark img').src", "document.querySelector('.print-head img').src")

# ---------- scope every explorer rule to #xp so it cannot touch the site's header or footer ----------
css = re.sub(r'/\* header \(main site, solid state\) \*/.*?/\* layout \*/', '/* layout */', css, flags=re.S)
def split_top(t):
    out, i, n = [], 0, len(t)
    while i < n:
        j = t.find('{', i)
        if j < 0: break
        sel = t[i:j].strip(); depth, k = 1, j + 1
        while depth and k < n:
            depth += {'{': 1, '}': -1}.get(t[k], 0); k += 1
        out.append((sel, t[j + 1:k - 1])); i = k
    return out
def pre(sel):
    s = re.sub(r'/\*.*?\*/', '', sel, flags=re.S).strip()
    parts = [p.strip() for p in re.split(r',(?![^()]*\))', s) if p.strip()]
    res = []
    for p in parts:
        if p in (':root', 'body'): res.append('#xp')
        elif p == 'html': res.append('html')
        elif p == 'html,body': res.append('#xp')
        elif p.startswith('.app'): res.append('#xp' + p[4:])
        else: res.append('#xp ' + p)
    return ','.join(res)
def scope(t):
    out = []
    for sel, inner in split_top(t):
        s = re.sub(r'/\*.*?\*/', '', sel, flags=re.S).strip()
        if s.startswith('@keyframes'): out.append(f'{s}{{{inner}}}')
        elif s.startswith('@media') or s.startswith('@supports'): out.append(f'{s}{{{scope(inner)}}}')
        else: out.append(f'{pre(s)}{{{inner}}}')
    return '\n'.join(out)
css = scope(css)
css = css.replace('#xp{overflow:hidden}', '#xp{}').replace('html,body{height:100%}', '')
css += '''
/* the explorer sits in the page under concept-v3's fixed header, with the footer below it */
#xp{--hdr:68px;position:relative;inset:auto;margin-top:var(--hdr);height:calc(100vh - var(--hdr));min-height:560px;border-bottom:1px solid var(--line);font-size:15px;line-height:1.5;text-align:left}
#xp h1,#xp h2,#xp h3{margin:0;font-family:inherit}
#xp p{margin:0}
#xp a{text-decoration:none}
#xp .btn{text-transform:none;letter-spacing:0;box-shadow:none}
#xp .sl-n{background:var(--green);color:#fff;border-radius:999px;min-width:20px;height:20px;display:inline-grid;place-items:center;font-size:11.5px;padding:0 6px}
#xp .mbtn[id=slBtn]:hover .sl-n{background:var(--green-hover)}
@media (max-width:900px){#xp{height:auto;min-height:0;display:grid;grid-template-rows:60vh auto;position:relative}}
@media print{.hdr,.mnav,footer{display:none!important}#xp{margin-top:0;height:auto;border:0}}
'''

page = (head.rstrip() + '\n<style>\n' + css + '\n</style>\n</head>\n' + chrome_top +
        '<main id="main">\n' + body + '\n</main>\n' + footer + '\n' +
        f'<script>window.PAGE={{"root": "{root}", "kind": "explorer"}};</script>\n<script src="{root}assets/js/v9.js"></script>\n'
        '<script>(function(){var h=document.getElementById("hdr");if(!h)return;var k=function(){if(!h.classList.contains("solid"))h.classList.add("solid")};k();new MutationObserver(k).observe(h,{attributes:true,attributeFilter:["class"]});})();</script>\n'
        '<script src="https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.js"></script>\n' + app_js + '\n</body>\n</html>\n')
open(DEST, 'w', encoding='utf-8').write(page)
print('wrote', DEST, len(page))
