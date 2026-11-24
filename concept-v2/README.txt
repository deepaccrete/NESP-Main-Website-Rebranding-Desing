Concept v6: USP-led redesign on fresh data
==========================================
site/   Open site/index.html (814 pages).
        Home: hero on field-verified data -> USP figures -> "Why this platform" (5 USPs) -> "Inside the field survey"
              -> Who are you? -> explore by state + site-finder -> webmaps -> data -> learning -> testimonials -> blog -> partners.
              OSIP removed from the homepage (still offered in the developer and investor next steps).
        New: communities/ (survey explorer + a printable page for each of the 769 surveyed communities),
             data-health/ (layer-by-layer duplicates, licences, link checks, distance recalculation).
etl/    Run in order: fetch_state_stats.py (now recalculates distance-to-grid for all 454,267 settlements),
        compute_insights.py, compute_extras.py, data_health.py. Planned to run nightly.
src/    make_build_v6.py patches build_v5.py into build_v6.py (every patch checked); pages_v5.py and pages_v6.py add pages.
Data pulled 23 November 2026 from data.nigeriase4all.gov.ng.
