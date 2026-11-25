# Line icons for the field-survey profiles (24px grid, stroke = currentColor). Plain SVG, no external library.
def _svg(inner):
    return f'<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{inner}</svg>'

SV_ICONS = {k: _svg(v) for k, v in {
    "grid": '<path d="M13 2 4 14h7l-1 8 9-12h-7z"/>',
    "gen": '<rect x="3" y="8" width="18" height="11" rx="1.5"/><path d="M7 8V5h4v3M12.5 10.5 10 14h3.5L11 17.5"/>',
    "fuel": '<path d="M4 21V5a2 2 0 0 1 2-2h6a2 2 0 0 1 2 2v16M3 21h12M7 7h4M14 9h2a2 2 0 0 1 2 2v5a1.5 1.5 0 0 0 3 0V8l-3-3"/>',
    "mill": '<circle cx="12" cy="12" r="3.5"/><path d="M12 2.5v3M12 18.5v3M2.5 12h3M18.5 12h3M5.3 5.3l2.1 2.1M16.6 16.6l2.1 2.1M5.3 18.7l2.1-2.1M16.6 7.4l2.1-2.1"/>',
    "shop": '<path d="M3 9 5 4h14l2 5M4 9v11h16V9M9 20v-6h6v6M3 9h18"/>',
    "pos": '<rect x="3" y="6" width="18" height="12" rx="1.5"/><path d="M3 10h18M7 15h4"/>',
    "phone": '<rect x="7" y="2" width="10" height="20" rx="1.5"/><path d="M11 18h2"/>',
    "craft": '<path d="M14.7 6.3a4 4 0 0 0-5.4 5.4L3 18l3 3 6.3-6.3a4 4 0 0 0 5.4-5.4l-2.5 2.5-2.4-.6-.6-2.4z"/>',
    "health": '<rect x="4" y="4" width="16" height="16" rx="2"/><path d="M12 8v8M8 12h8"/>',
    "school": '<path d="M2 9l10-5 10 5-10 5zM6 11v5c3 2 9 2 12 0v-5"/>',
    "bank": '<path d="M3 10l9-6 9 6M5 10v8M9.5 10v8M14.5 10v8M19 10v8M3 21h18"/>',
    "money": '<path d="M3 7h15a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H3zM3 7l12-4v4M16 13.5h2"/>',
    "signal": '<path d="M4 20v-3M9 20v-7M14 20V9M19 20V4"/>',
    "truck": '<path d="M1.5 6h12.5v10H1.5zM14 9h4l3.5 3.5V16H14"/><circle cx="5.5" cy="18" r="2"/><circle cx="17.5" cy="18" r="2"/>',
    "moto": '<circle cx="5" cy="17" r="3"/><circle cx="19" cy="17" r="3"/><path d="M5 17l4-6h5l2 6M13 11l2-3h3"/>',
    "crop": '<path d="M12 21V11M12 11C12 7 9 5 5 5c0 4 3 6 7 6zM12 13.5c0-4 3-6.5 7-6.5 0 4-3 6.5-7 6.5z"/>',
    "market": '<rect x="3" y="5" width="18" height="16" rx="1.5"/><path d="M3 9h18M8 3v4M16 3v4"/>',
    "house": '<path d="M3 11l9-7 9 7M5 10v10h14V10M10 20v-5h4v5"/>',
    "income": '<path d="M12 3v18M16 7h-6a3 3 0 0 0 0 6h4a3 3 0 0 1 0 6H8"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
    "pin": '<path d="M12 21s7-6.2 7-12a7 7 0 0 0-14 0c0 5.8 7 12 7 12z"/><circle cx="12" cy="9" r="2.5"/>',
    "sub": '<rect x="4" y="9" width="16" height="11" rx="1"/><path d="M8 9V5h8v4M12 12l-2 3h4l-2 3"/>',
    "cal": '<rect x="3" y="5" width="18" height="16" rx="1.5"/><path d="M3 9h18M8 3v4M16 3v4M8 13h3"/>',
}.items()}
