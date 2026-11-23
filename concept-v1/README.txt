Nigeria SE4ALL - website concept v2 (data-led)
==============================================
site/   Static site. Open site/index.html. Key pages: index.html, states/index.html, states/nasarawa/index.html
        (all 37 state profiles are generated from the same template).
etl/    fetch_state_stats.py - pulls public WFS layers from data.nigeriase4all.gov.ng and computes per-state
        figures (planned to run nightly). Output: data/*.json
src/    build_v2.py + assets - generates site/ from data/. Run:  python3 etl/fetch_state_stats.py --out data && python3 src/build_v2.py
Notes:  Map overlays are live GeoServer WMS tiles; boundaries/figures come from data/. Photos are hotlinked from nigeriase4all.gov.ng.
        Data pulled 20 Nov 2026.
