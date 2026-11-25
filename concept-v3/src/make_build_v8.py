# build_v8.py = build_v7.py + checked patches: combined mini-grid hub and map-first developer/investor workspaces.
# Also writes v8.js (v7.js + ws.js) and v8.css (v7.css + ws.css). Run make_build_v7.py first.
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, "build_v7.py"), encoding="utf-8").read()
def P(old, new, count=1):
    global src
    n = src.count(old)
    if n != count: sys.exit(f"build_v7.py: patch failed ({n}x): {old[:110]!r}")
    src = src.replace(old, new)

P('"v7.css"', '"v8.css"', count=2); P('"v7.js"', '"v8.js"', count=2)
P('assets/css/v7.css', 'assets/css/v8.css'); P('assets/js/v7.js', 'assets/js/v8.js', count=2)
P('''f'<a href="{{R}}projects/index.html">Projects</a>''', '''f'<a href="{{R}}minigrids/index.html">Mini-grids</a><a href="{{R}}projects/index.html">Projects</a>''')
P('''<a href="{{R}}projects/index.html">Electrification projects</a>''', '''<a href="{{R}}minigrids/index.html">Mini-grid map</a><a href="{{R}}projects/index.html">Electrification projects</a>''')
P('''<div><b>{f0(ALL_MG_N)}</b><span>mini-grids recorded (platform and NEP)</span></div>''', '''<div><b>{f0(len(MGS))}</b><span>mini-grids recorded (three sources)</span></div>''')
P('s = s[:i] + usp_sections() + NEW + projects_strip() + s[i:]', 's = s[:i] + usp_sections() + NEW + minigrid_strip() + s[i:]')
P('exec(open(os.path.join(HERE, "pages_v7.py"), encoding="utf-8").read())',
  'exec(open(os.path.join(HERE, "pages_v7.py"), encoding="utf-8").read())\nexec(open(os.path.join(HERE, "pages_v8.py"), encoding="utf-8").read())')
P("have no mini-grid recorded in either the platform or the NEP project map.</p>", "have no mini-grid recorded in any of the three public sources.</p>")
P('data_health(); projects_page()', 'data_health(); projects_page(); minigrid_hub()')
P('Data</a><a href="{ORIG}/blog">Blog</a><a href="{ORIG}/about">About</a>', 'Data</a><a href="{ORIG}/about">About</a>')   # Blog stays in the footer and mobile menu
open(os.path.join(HERE, "build_v8.py"), "w", encoding="utf-8").write(src)

js = open(os.path.join(HERE, "assets", "js", "v7.js"), encoding="utf-8").read(); k = js.rstrip().rfind("})();")
open(os.path.join(HERE, "assets", "js", "v8.js"), "w", encoding="utf-8").write(js[:k] + open(os.path.join(HERE, "assets", "js", "ws.js"), encoding="utf-8").read() + "\n})();\n")
open(os.path.join(HERE, "assets", "css", "v8.css"), "w", encoding="utf-8").write(
    open(os.path.join(HERE, "assets", "css", "v7.css"), encoding="utf-8").read() + "\n" + open(os.path.join(HERE, "assets", "css", "ws.css"), encoding="utf-8").read())
print("build_v8.py, v8.js, v8.css written")
