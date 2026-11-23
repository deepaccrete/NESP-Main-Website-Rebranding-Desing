---
name: Nigeria Electrification Atlas
description: The National Atlas — an authoritative, map-first geospatial record of Nigeria's electrification
colors:
  green: "#065F46"
  green-hover: "#064E3B"
  night: "#043D2E"
  leaf: "#A3D376"
  leaf-soft: "#CFE9B8"
  slate: "#1E4E79"
  slate-accent: "#6FA3D6"
  amber: "#E8A317"
  amber-ink: "#9A6A06"
  ink: "#0F172A"
  ink-2: "#475569"
  field: "#F4F7F5"
  footer: "#E6EDE8"
  ghost: "#D3DED6"
  line: "#E5E7EB"
  white: "#FFFFFF"
typography:
  display:
    fontFamily: "Inter, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
    fontSize: "54px"
    fontWeight: 600
    lineHeight: 1.06
    letterSpacing: "-0.025em"
  headline:
    fontFamily: "Inter, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
    fontSize: "36px"
    fontWeight: 600
    lineHeight: 1.15
    letterSpacing: "-0.01em"
  title:
    fontFamily: "Inter, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
    fontSize: "22px"
    fontWeight: 500
    lineHeight: 1.3
    letterSpacing: "0em"
  body:
    fontFamily: "Inter, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
    fontSize: "17px"
    fontWeight: 400
    lineHeight: 1.6
    letterSpacing: "0em"
  label:
    fontFamily: "Inter, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
    fontSize: "12.5px"
    fontWeight: 600
    lineHeight: 1.2
    letterSpacing: "0.12em"
rounded:
  sm: "8px"
  md: "10px"
  lg: "14px"
  xl: "16px"
  xxl: "18px"
  pill: "999px"
spacing:
  xs: "8px"
  sm: "12px"
  md: "20px"
  lg: "32px"
  xl: "48px"
  section: "96px"
components:
  button-primary:
    backgroundColor: "{colors.green}"
    textColor: "{colors.white}"
    rounded: "{rounded.md}"
    padding: "14px 22px"
    height: "48px"
  button-primary-hover:
    backgroundColor: "{colors.green-hover}"
    textColor: "{colors.white}"
    rounded: "{rounded.md}"
    padding: "14px 22px"
  button-outline:
    backgroundColor: "{colors.white}"
    textColor: "{colors.green}"
    rounded: "{rounded.md}"
    padding: "14px 22px"
    height: "48px"
  button-leaf:
    backgroundColor: "{colors.leaf}"
    textColor: "{colors.night}"
    rounded: "{rounded.md}"
    padding: "14px 22px"
    height: "48px"
  button-ghost:
    backgroundColor: "transparent"
    textColor: "{colors.white}"
    rounded: "{rounded.md}"
    padding: "14px 22px"
    height: "48px"
  button-download:
    backgroundColor: "{colors.white}"
    textColor: "{colors.green}"
    rounded: "{rounded.sm}"
    padding: "9px 14px"
  chip:
    backgroundColor: "{colors.field}"
    textColor: "{colors.ink}"
    rounded: "{rounded.pill}"
    padding: "5px 10px"
  card:
    backgroundColor: "{colors.white}"
    textColor: "{colors.ink}"
    rounded: "{rounded.xl}"
    padding: "26px"
  nav-link:
    backgroundColor: "transparent"
    textColor: "{colors.white}"
    padding: "6px 0"
---

# Design System: Nigeria Electrification Atlas

## Overview

**Creative North Star: "The National Atlas"**

This is the authoritative, map-first record of who in Nigeria has power and who does not. It should feel like opening the definitive national reference — official, but never cold. The visual world is built from two things the platform actually traffics in: **land** (a deep forest-green cover, the colour of the country's electrification mission) and **data layers** (clean white plates that lift off the page, maps that carry the eye, numbers set in confident type). Dark green establishes authority at the top of every page; a light, almost paper-white body carries the evidence below it.

The system runs on restraint. One typeface (Inter) does all the work; one green carries nearly all the brand weight; depth is gentle and functional. Against that calm institutional base, a single bright **leaf-green** is the spark — used sparingly, mostly on dark grounds, to mark what's live, what's current, what matters now. Sector work is colour-coded with discipline: slate-blue for the power sector, amber for solar home systems, leaf-green for mini-grids and the default. These are signals, not decoration.

The platform serves developers, government planners, DisCos, researchers and students together, often on mobile and on variable Nigerian networks. So the craft shows as precision and legibility: generous line length, tabular numerals on every statistic, honest sourcing lines under charts, and interactions that reward without distracting. Nothing here is loud for its own sake. The confidence comes from clarity.

**Key Characteristics:**
- Deep forest-green authority bands over a light, paper-white body.
- One typeface (Inter), hierarchy built from size, weight and tracking.
- Flat pages; white cards float on soft green-tinted shadows and lift on hover.
- A single bright leaf-green accent, used rarely, as the "live / now" signal.
- Disciplined sector colour-coding: slate = power, amber = solar, leaf = mini-grid/default.
- Map, data-layer and chart motifs as the recurring visual language.

## Colors

A restrained palette: deep greens for authority, a paper-white body, one bright accent, and two reserved sector signals.

### Primary
- **Forest Green** (`#065F46`): The brand's load-bearing colour. Primary buttons, links, active states, section kickers, icon accents, chart series. The default brand voice on any light surface.
- **Deep Forest** (`#064E3B`): The pressed/hover state of Forest Green on buttons and interactive greens.
- **Midnight Pine** (`#043D2E`): The darkest green. Grounds the hero gradients, dark stat cards, stakeholder monograms, and the soft shadow tint (`rgba(4,61,46,…)`) used under every floating card.

### Secondary
- **Leaf** (`#A3D376`): The bright spark. Used sparingly and almost always on dark grounds — the pulsing "live / now" dot, hero highlight text, accent underlines, the leaf CTA button on dark bands, focus outlines. Its rarity is the point.
- **Leaf Soft** (`#CFE9B8`): A pale wash of leaf for soft tints, gradient midpoints, and gentle icon chips.

### Tertiary (sector signals)
- **Slate Blue** (`#1E4E79`) / **Slate Accent** (`#6FA3D6`): The power-sector signal. Keys power-sector chips, dots, and the power-sector page accent bar. Never used outside power-sector context.
- **Amber** (`#E8A317`) / **Amber Ink** (`#9A6A06`): The solar-home-systems signal. Keys SHS chips, dots, and the SHS page accent bar. Never used outside solar context.

### Neutral
- **Ink** (`#0F172A`): Primary text and headings.
- **Ink Muted** (`#475569`): Secondary text, captions, table headers, sources, metadata.
- **Field** (`#F4F7F5`): The soft light-green-grey panel fill — alternating sections, chip backgrounds, icon tiles, intro callouts.
- **Footer Mist** (`#E6EDE8`): The slightly deeper tint reserved for the footer field.
- **Ghost** (`#D3DED6`): The faint footer emblem and the pale map-plate strokes in the data-layer visuals.
- **Line** (`#E5E7EB`): Hairline borders, dividers, table rules, card outlines.
- **White** (`#FFFFFF`): The page body and every floating card surface.

### Named Rules
**The One Green Rule.** Forest Green (`#065F46`) is the only accent that appears freely on light surfaces. Everything else — leaf, slate, amber — is reserved for a specific job. If you reach for a second colour "to add interest," stop: use green, or use white space.

**The Live-Leaf Rule.** Bright Leaf (`#A3D376`) is the "now" signal, not a fill. It belongs to pulsing status dots, hero highlight words, focus rings, and the leaf CTA on dark bands — surfaces where it reads as energy. It should never become a large flat background on a light page.

**The Sector Signal Rule.** Slate = power sector, amber = solar home systems, leaf-green = mini-grids and the default. A sector colour appears only to mark that sector's content (a chip, a dot, a page accent bar). It is never decoration and never mixed across sectors.

## Typography

**Display / Body / Label Font:** Inter (with `"Segoe UI", Roboto, Helvetica, Arial, sans-serif` fallbacks), loaded at weights 400 / 500 / 600 / 700.

**Character:** One humanist sans does everything. The personality is institutional and modern — clear at a glance on a phone over a slow connection, confident enough to carry a 54px page headline. Hierarchy is built entirely from size, weight, and negative tracking on large sizes, never from a second typeface.

### Hierarchy
- **Display** (600, 54px on inner-page heroes / `clamp(32px, 3.2vw, 46px)` on the homepage hero, line-height ~1.06, letter-spacing −0.025em): Page and hero headlines. Balanced wrapping (`text-wrap: balance`); on the homepage hero the key phrase is highlighted with a leaf gradient fill.
- **Headline** (600, 36px, line-height 1.15, −0.01em): Section titles (`h2`). Drops to 28px on tablet, 25px on phones.
- **Title** (500–600, 22px, line-height ~1.3): Subsection and card headings (`h3`). Card titles shift to 600 at smaller sizes.
- **Body** (400, 17px, line-height 1.6): Default prose. Long-form reading (`.article`, `.prose`) steps up to 18px / line-height 1.75 and is capped at 70–74ch. Drops to 16px below 480px.
- **Label / Eyebrow / Kicker** (600, 12.5px, letter-spacing 0.12–0.14em, UPPERCASE): Table headers and overline labels. The *eyebrow/kicker-above-a-heading* use is a **legacy pattern** — keep the instances already in the pages, but don't add new ones (often paired with a small leaf or green dot).
- **Statistic** (700, 28–44px, `font-variant-numeric: tabular-nums`, −0.02em): KPI and stat numbers. Superscripts (e.g. `+`, `%`) are set in leaf or green at ~0.55em.

### Named Rules
**The One Typeface Rule.** Inter is the entire type system. Never introduce a second family for "contrast" — contrast comes from weight (400 vs 600/700), size, and tracking. A serif or display face would break the institutional voice.

**The Tabular Numbers Rule.** Every figure that represents data — KPIs, stats, file sizes, years, chart labels — uses `font-variant-numeric: tabular-nums` so columns align and numbers don't jitter between states.

## Layout

A centred `1240px` max-width container (`.wrap`) with `32px` side padding (`20px` ≤640px, `16px` ≤480px). Vertical rhythm is set by the section unit: `96px` top/bottom (`.sec`), compressing to `64px` ≤640px and `52px` ≤480px. Alternating sections use the Field (`#F4F7F5`) fill or a `field → white` gradient tint to separate content without borders.

Content is organised on predictable grids: 4-up for KPIs, tools, and overview cards; 3-up for columns and blog cards; 2-up (`1.05fr / 1fr`, `1.02fr / .98fr`) for the data-portal and page-hero split layouts; and a `340px / 1fr` sticky-sidebar grid for dataset tables and long-form articles. Grid gaps run `16–24px` within card rows and `48–72px` between major columns.

**Responsive behaviour** collapses at four breakpoints: `1280px` (header text trims), `1100px` (two-column layouts stack, main nav becomes a burger menu, sticky sidebars go static), `640px` (most grids go single-column, a sticky bottom CTA appears), and `480px` (base font drops to 16px, padding tightens). Section anchors reserve an `80px` scroll margin to clear the fixed `68px` header.

## Elevation & Depth

**Flat page, floating cards.** Backgrounds are flat — white, Field tint, or a dark green gradient. Depth exists only on discrete objects: white cards float on soft, green-tinted shadows (`rgba(4,61,46,…)`, never neutral black) and lift further on hover. The shadow colour is deliberately the brand's midnight pine, so elevation reads as part of the world rather than a generic drop shadow. Dark hero bands add atmospheric depth through layered radial-gradient glows and a faint dotted grid, not through shadow.

### Shadow Vocabulary
- **Card rest** (`box-shadow: 0 14px 40px rgba(4,61,46,.16), 0 1px 0 #E5E7EB`): KPI and overview cards at rest — a soft green lift plus a crisp hairline.
- **Card hover** (`box-shadow: 0 24px 54px rgba(4,61,46,.22), 0 1px 0 #E5E7EB`): The raised state, paired with `translateY(-5px)`.
- **Tool / tile hover** (`box-shadow: 0 18px 40px rgba(4,61,46,.12)`): Lighter lift for bordered tool and post cards, paired with `translateY(-4px)`.
- **Dropdown / menu** (`box-shadow: 0 20px 50px rgba(4,61,46,.18), 0 0 0 1px #E5E7EB`): Floating nav menus and popovers.
- **Browser frame** (`box-shadow: 0 30px 80px rgba(0,0,0,.35)`): The one place near-black shadow is correct — screenshot "browser frame" mockups on dark hero grounds, where a green shadow would disappear.
- **Header seam** (`box-shadow: 0 1px 0 #E5E7EB`): The solid-scrolled header's single hairline.

### Named Rules
**The Flat-By-Default Rule.** Surfaces are flat at rest unless they are a distinct floating object (a card, a menu, a frame). Shadows signal "this is a separate thing" or respond to hover/focus — they are never applied to sections, bands, or text blocks for ambience.

**The Green-Shadow Rule.** Card and UI shadows are tinted with `rgba(4,61,46,…)` (midnight pine), not black. Reserve neutral-black shadow only for mockup frames sitting on dark grounds.

## Shapes

Soft, confident rounding throughout — nothing sharp, nothing fully circular except status dots and avatars. The radius scale maps to purpose: **`8px`** for small icon tiles and download buttons, **`10px`** for primary buttons and dropdown rows, **`14px`** for standard cards, tool tiles, and tables, **`16px`** for KPI/overview cards, and **`18–24px`** for large feature blocks, course panels, and the testimonial card. **Pills (`999px`)** carry status: chips, eyebrow badges, sub-nav tabs, filter toggles, and the "open map" control.

Borders are hairline (`1–1.5px`, `#E5E7EB`) and define bordered cards, tables, and inputs. Left-edge accent bars (`3–4px` leaf or green) mark stat groups, callouts, and the top of KPI cards on reveal — this is a **legacy pattern**: keep the existing bars, but don't introduce new ones. Recurring geometry comes from the subject: tilted 3D "data layer" plates, dotted/line map-grid fills, and radial glow halos behind maps and dark bands.

## Components

### Buttons
- **Shape:** Gently rounded (`10px`), `48px` min-height, `14px 22px` padding, weight 600, with an 8px gap for inline icons. Compact variants (header, table, download) use `38–40px` height and smaller padding.
- **Primary:** Solid Forest Green (`#065F46`) on white text → Deep Forest (`#064E3B`) on hover. On dark hero/band grounds the primary swaps to the **Leaf** button (leaf fill, midnight-pine text) so the CTA stays legible and energetic.
- **Outline:** Transparent/white with a Forest Green border and text; fills with a 6%-green wash on hover.
- **Ghost:** Transparent with a translucent white border, for dark grounds; border brightens and a faint white wash appears on hover.
- **Hover / Focus / Active:** `.18s` transitions on background/transform/border. Hero and card CTAs add `translateY(-2px)` with a leaf-tinted glow. Active state is `translateY(1px)`. Focus-visible is a `3px` Forest Green (`#065F46`) outline with `3px` offset on light surfaces; on dark green grounds (hero and CTA bands) the ring switches to Leaf so it keeps contrast against the dark.

### Chips & Tags
- **Style:** Pill (`999px`), Field background, ink text, 600 weight, `12.5px`, with a leading status dot. The dot colour carries the sector signal (green default, slate for power, amber for solar).
- **Filter variant:** `1.5px` bordered pill toggles; `aria-pressed="true"` fills solid green with a white dot. On hover, border and text shift to green.

### Cards / Containers
- **Corner Style:** `14–16px` for standard cards; `18–24px` for feature/course/testimonial blocks.
- **Background:** White on light sections; Field for intro callouts and icon tiles; the `green → night` gradient for dark CTA bands and stat cards.
- **Shadow Strategy:** See Elevation — green-tinted soft lift at rest, deeper lift + `translateY` on hover. Bordered tool/post cards use a `1px` line at rest and drop the border into a shadow on hover.
- **Border:** `1px #E5E7EB` where a card sits on white; omitted where the soft shadow already separates it.
- **Internal Padding:** `20–26px` standard; `40–48px` for large feature and course panels.

### Dataset Table
- **Style:** White, `14px` radius, `1px` line rules, header row in `13px` muted uppercase-ish labels. Rows hover to a faint green tint (`#F8FBF9`). Numeric columns are tabular and right/centre aligned; the download column carries the outline **download button** (`.btn-dl`) that inverts to solid green on hover.
- **Responsive:** Secondary columns, icon tiles, and button labels drop out progressively below 640px.

### Navigation
- **Header:** Fixed `68px` bar, transparent white-text over heroes, switching to a blurred white `.solid` state on scroll (ink text, hairline seam). Dropdown mega-menus are white, `14px` radius, with Field-tinted icon tiles.
- **Links:** `15px`, weight 500, 90% opacity, with a `2px` bottom border that appears on hover/active (`.on`).
- **Sub-nav:** Sticky pill tabs under the header; the active tab fills solid green.
- **Mobile:** Below 1100px the main nav collapses into a burger-triggered full-width white panel with grouped sections.

### History Timeline (About page)
- **Style:** A vertical list with a continuous `2px` Line rail down the left; each entry is a two-column grid (`150px` year / `1fr` body) sitting `34px` right of the rail.
- **Markers:** A `16px` white dot ringed in `3px` Forest Green per entry. The current entry (`.now`) fills the dot with Leaf and adds a `5px` leaf halo (`rgba(163,211,118,.3)`).
- **Type:** The year (`.when`) is Forest Green, 700, `15px`, tabular numerals; the entry title is `17px` ink; the body is `15.5px` Ink Muted.
- **Responsive:** Below 640px the year/body grid collapses to a single column and the left inset tightens to `30px`.

### Request / Share Data Rows (About page)
- **Style:** A vertical stack of bordered white cards (`14px` radius, `1px` Line), each a `1fr auto` grid — title (`17px`) and muted description (`15px`) on the left, a green `.link` action spanning both rows on the right.
- **Hover:** Border shifts to Forest Green with a soft green lift (`0 12px 28px rgba(4,61,46,.1)`, `translateY(-2px)`).
- **Focus:** `3px` Forest Green outline with `3px` offset on the whole card.
- **Responsive:** Below 640px the card goes single-column and the action drops beneath the text.

### Signature — Data Layer Stack & Map Motifs
The defining custom components: the tilted 3D "open data layers" stack (map plates that lift and separate on hover/reveal), the browser-frame webmap mockups (perspective-rotated with a leaf glow halo), floating map tooltips with leaf headings, and SVG charts with dashed target lines, tabular labels, and source attributions. These carry the "Atlas" metaphor and should lead inner-page heroes and data sections.

## Do's and Don'ts

### Do:
- **Do** lead with Forest Green (`#065F46`) for all primary action and brand emphasis on light surfaces; let white space do the rest.
- **Do** reserve bright Leaf (`#A3D376`) for "live/now" signals, hero highlights, focus rings, and the CTA on dark bands — small doses only.
- **Do** key sector content with its signal colour (slate = power, amber = solar, leaf = mini-grid/default) and nothing else.
- **Do** tint card shadows with `rgba(4,61,46,…)`, and pair every hover lift with a matching `translateY`.
- **Do** set every data figure in Inter with `font-variant-numeric: tabular-nums`.
- **Do** keep long-form reading to 70–74ch and step body type up to 18px/1.75 in articles.
- **Do** give every interactive element a `3px` focus outline: Forest Green (`#065F46`) on light surfaces, Leaf only on dark green grounds. WCAG 2.2 AA requires a 3:1 focus indicator, and leaf-on-white is ~1.6:1.
- **Do** honour `prefers-reduced-motion` (reveals and loops already disable under it).

### Don't:
- **Don't** introduce a second typeface — build contrast from Inter's weights, sizes, and tracking.
- **Don't** add a new accent colour "for variety"; the palette is deliberately narrow.
- **Don't** flood a light surface with a large flat leaf-green fill — it's a spark, not a background.
- **Don't** use neutral-black shadows on light surfaces (green-tinted only); reserve black shadow for mockup frames on dark grounds.
- **Don't** apply shadows to sections, bands, or text blocks for ambience — depth belongs to discrete floating objects.
- **Don't** add new eyebrow/kicker labels above headings or new left-edge accent bars — both are legacy; retain existing instances but don't extend the pattern.
- **Don't** reference "SE4ALL" or the global SEforALL initiative to describe the platform; keep REA as the primary brand with the Federal Ministry of Power as policy partner. (Historical blog/event names stay as published.)
