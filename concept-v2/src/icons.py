# One consistent line-icon set (24px grid, 1.8 stroke, round caps) for roles and webmaps.
def _svg(paths, size=22):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{paths}</svg>')

ROLE_ICONS = {
    # mini-grid developer: solar panel with a bolt
    "developer": _svg('<path d="M3 14l2.5-8h13L21 14z"/><path d="M4.4 10h15.2M9 6l-1 8M15 6l1 8"/><path d="M12 14v3M8 21h8M12 17l-1.5 2.2h3L12 21.4"/>'),
    # investor: rising chart with coin
    "investor": _svg('<path d="M3 20h18"/><path d="M5 16l4-4 3 3 6-7"/><path d="M14 8h4v4"/><circle cx="6.5" cy="6.5" r="2.5"/>'),
    # state government: columned building
    "state": _svg('<path d="M3 10l9-6 9 6"/><path d="M5 10v8M9.5 10v8M14.5 10v8M19 10v8"/><path d="M3 21h18M4 18h16"/>'),
    # researcher / data user: database with magnifier
    "researcher": _svg('<ellipse cx="10" cy="5.5" rx="6.5" ry="2.5"/><path d="M3.5 5.5v9c0 1.4 2.9 2.5 6.5 2.5"/><path d="M16.5 5.5V10"/><path d="M3.5 10c0 1.4 2.9 2.5 6.5 2.5"/><circle cx="17" cy="16" r="3"/><path d="M19.2 18.2L21.5 20.5"/>'),
    # student / GIS career: graduation cap with map pin
    "learner": _svg('<path d="M2 9l10-5 10 5-10 5z"/><path d="M6 11v4.5c0 1.4 2.7 2.5 6 2.5s6-1.1 6-2.5V11"/><path d="M22 9v5"/>'),
}

WEBMAP_ICONS = {
    # off-grid mini-grid: village roof + sun, no line
    "offgrid": _svg('<circle cx="17.5" cy="6" r="2.5"/><path d="M17.5 1.5v.8M21.7 6h-.8M14.1 6h-.8M20.5 3l-.6.6"/><path d="M3 12l6-5 6 5"/><path d="M5 11v9h8v-9"/><path d="M8 20v-4h2v4"/>'),
    # interconnected mini-grid: two nodes joined to the grid
    "interconnected": _svg('<circle cx="5" cy="6" r="2.5"/><circle cx="19" cy="6" r="2.5"/><circle cx="12" cy="18" r="2.5"/><path d="M7.5 6h9M6.3 8.2l4.4 7.6M17.7 8.2l-4.4 7.6"/>'),
    # power sector: transmission pylon
    "power": _svg('<path d="M12 2l-5 20M12 2l5 20"/><path d="M6 8h12M5 13h14"/><path d="M8.3 8l7.6 5M15.7 8L8.1 13"/><path d="M9.5 18h5"/>'),
    # solar home systems: house with panel
    "shs": _svg('<path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10"/><path d="M9 13h6l1 4H8z"/><path d="M11 13l-.5 4M13 13l.5 4"/>'),
}

CHEVRON = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>'
EXT = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M7 17 17 7M9 7h8v8"/></svg>'

USP_ICONS = {
    "survey": _svg('<rect x="5" y="3.5" width="14" height="18" rx="2"/><path d="M9 3.5h6v3H9z"/><path d="M8.5 11l1.5 1.5 3-3M8.5 16.5h7"/>', 26),
    "grid": _svg('<path d="M12 2l-5 20M12 2l5 20"/><path d="M6 8h12M5 13h14"/><path d="M8.3 8l7.6 5M15.7 8L8.1 13"/><path d="M9.5 18h5"/>', 26),
    "answers": _svg('<path d="M4 5h16v11H9l-5 4z"/><path d="M8 9h8M8 12h5"/>', 26),
    "open": _svg('<ellipse cx="12" cy="5.5" rx="7" ry="2.5"/><path d="M5 5.5v13c0 1.4 3.1 2.5 7 2.5s7-1.1 7-2.5v-13"/><path d="M5 12c0 1.4 3.1 2.5 7 2.5s7-1.1 7-2.5"/>', 26),
    "skills": _svg('<path d="M2 9l10-5 10 5-10 5z"/><path d="M6 11v4.5c0 1.4 2.7 2.5 6 2.5s6-1.1 6-2.5V11"/><path d="M22 9v5"/>', 26),
}
