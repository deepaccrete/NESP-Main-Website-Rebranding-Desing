# build_v9.py = build_v8.py + checked patches: interactive field survey, two developer site finders and a comparison page.
# Run make_build_v7.py and make_build_v8.py first. Writes v9.js (v8.js + sv.js) and v9.css (v8.css + sv.css).
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, "build_v8.py"), encoding="utf-8").read()
def P(old, new, count=1):
    global src
    n = src.count(old)
    if n != count: sys.exit(f"build_v8.py: patch failed ({n}x): {old[:110]!r}")
    src = src.replace(old, new)
P('"v8.css"', '"v9.css"', count=2); P('"v8.js"', '"v9.js"', count=2)
P('assets/css/v8.css', 'assets/css/v9.css'); P('assets/js/v8.js', 'assets/js/v9.js', count=2)
P('''<a href="{{R}}minigrids/index.html">Mini-grid map</a>''',
  '''<a href="{{R}}minigrids/index.html">Mini-grid map</a><a href="{{R}}for/developers/index.html">Site finder</a><a href="{{R}}for/developers/world-bank/index.html">Site finder (World Bank DRE data)</a><a href="{{R}}for/developers/compare/index.html">Compare the site finders</a>''')
P('exec(open(os.path.join(HERE, "pages_v8.py"), encoding="utf-8").read())',
  'exec(open(os.path.join(HERE, "pages_v8.py"), encoding="utf-8").read())\nexec(open(os.path.join(HERE, "pages_v9.py"), encoding="utf-8").read())')
P('projects_page(); minigrid_hub()', 'projects_page(); minigrid_hub(); compare_page()')
open(os.path.join(HERE, "build_v9.py"), "w", encoding="utf-8").write(src)
js = open(os.path.join(HERE, "assets", "js", "v8.js"), encoding="utf-8").read(); k = js.rstrip().rfind("})();")
open(os.path.join(HERE, "assets", "js", "v9.js"), "w", encoding="utf-8").write(js[:k] + open(os.path.join(HERE, "assets", "js", "sv.js"), encoding="utf-8").read() + "\n})();\n")
open(os.path.join(HERE, "assets", "css", "v9.css"), "w", encoding="utf-8").write(
    open(os.path.join(HERE, "assets", "css", "v8.css"), encoding="utf-8").read() + "\n" + open(os.path.join(HERE, "assets", "css", "sv.css"), encoding="utf-8").read())
print("build_v9.py, v9.js, v9.css written")
