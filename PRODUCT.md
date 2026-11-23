# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Four audiences, served together; none is subordinate (confirmed by the product owner, Nov 2026):

- **Developers and investors**: mini-grid and solar home system developers, financiers and project developers looking for viable sites, demand, grid proximity and downloadable data before committing to a project.
- **Government planners**: the Rural Electrification Agency (REA), the Federal Ministry of Power (FMP) and state energy teams doing electrification planning and tracking national targets.
- **DisCos and regulators**: distribution companies and NERC using grid asset and coverage data.
- **Researchers, students and volunteers**: academics, GIS learners and mapathon volunteers who use the open data and the learning platform.

## Product Purpose

The national, government-owned geospatial data platform for electrification planning in Nigeria. It publishes field-collected and modelled data (MV grid, settlements, buildings, mini-grids, power plants, DisCo areas), interactive webmaps built on that data, open dataset downloads, and training, so that planning and investment decisions rest on the same evidence.

Success means stakeholders across the sector use the platform as their reliable source of electrification data, and REA can keep it current after NESP's implementation period ends.

## Positioning

It is the only platform holding NESP's field-collected national evidence base: medium-voltage (11 kV and 33 kV) grid mapped across all 36 states and the FCT, and on-site surveys of 700 rural settlements. It is owned and operated by REA, a government agency, not a commercial or donor-branded tool.

The platform is **not affiliated with the global Sustainable Energy for All (SEforALL) initiative**. The old name caused that confusion; removing it is the main reason for the rebrand. The new name is Nigeria Electrification Atlas.

## Operating Context

- Previously branded "Nigeria SE4ALL" at nigeriase4all.gov.ng (Version 3 launched 2022 by NESP). Being rebranded and handed over to REA as operational owner; launch and handover event planned for 3 December 2026 in Abuja.
- The interactive webmaps live at apps.nigeriase4all.gov.ng, datasets at data.nigeriase4all.gov.ng, training at learning.nigeriase4all.gov.ng. These subdomains are expected to move with the new domain.
- REA will be responsible for management, technical maintenance and periodic data updates, and for how stakeholders contribute and request data.
- Sister platform: OSIP, the One-Stop Investment Platform for renewable energy and energy efficiency (regulation, licensing, finance). This platform answers "where to build"; OSIP answers "how to invest".

## Capabilities and Constraints

- Sector areas: Mini-grids (off-grid and interconnected locators), Power sector (DisCo coverage, transmission network, 30:30:30 target progress), Solar home systems (rural market analysis).
- Open data downloads under a Creative Commons licence; blog; learning platform; accreditation page.
- This repository is a static HTML/CSS/JS design prototype for the rebrand; the production platform is a separate codebase.
- **Name:** the platform's new name is **Nigeria Electrification Atlas** (confirmed Nov 2026). Before it, the platform was called Nigeria SE4ALL.
- **Undecided:** the new web address. Live links keep the current nigeriase4all.gov.ng addresses, and the data citation uses the placeholder `[Web address]`, until the domain changes (`sh rename-platform.sh "Nigeria Electrification Atlas" new-domain`).
- **Undecided:** the REA contact email for the site (placeholder `[contact@rea.gov.ng]`).

## Brand Commitments

- REA is the owner and primary brand; the Federal Ministry of Power appears as policy partner.
- All communication materials carry the logos of NESP with its commissioning parties (European Union, German Cooperation / BMZ, GIZ) and REA.
- The name "SE4ALL" and links to the global SEforALL initiative must not be used to describe the platform. Historical blog posts and event names that used the old name (e.g. "Nigeria SE4ALL Mapathon") stay as published.

## Evidence on Hand

- Concept note and draft agenda for the rebrand and handover (17 Nov 2026).
- NESP III Terms of Reference (project docs).
- Real figures: MV grid mapped in all 36 states + FCT; 700 rural settlements surveyed on site; 280+ mapathon participants, 75,000+ buildings mapped by volunteers, 400+ mappers in the community.
- Real photos and screenshots in `assets/` (mapathon, mobile mapping, webmap screenshots, sector photos).
- Testimonials: only anonymous mapathon participant feedback exists. Named testimonials from developers, REA staff or investors do not exist yet and must not be invented.

## Product Principles

1. Data first: every section should lead to a map, a dataset or a method someone can use.
2. Government-owned and neutral: speak as REA's public service, not as a donor project or a global brand.
3. Plain language for mixed expertise: a developer, a state planner and a student should all find their way in.
4. Show the evidence: use real figures and real field imagery; never invent claims.
5. Built to be maintained: REA must be able to update content and data without the original team.

## Accessibility & Inclusion

WCAG 2.2 AA is required. Many users are on mobile and on variable network connections in Nigeria, so pages must stay usable on small screens and slow links.
