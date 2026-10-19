---
version: 1
slug: "app-py"
primary_target: "app.py"
related_targets: []
---

# Surface: app.py (Streamlit assessor UI)

Scope: the whole Streamlit UI in `app.py` (sidebar, Evidence / Run / Review & download / Charts tabs). Mode: Operate. UI-only: no change to Jev calls, questions, thresholds, decision logic or library content.

Task: one assessor moves a customer from evidence to a sendable docx, then checks Jev's judgments on Review (level, score cross-check, recommendations Jev was unsure about).

## Direction contract

THESIS: The tool should feel like a page inside SonarQube Server, not like a generic Streamlit app with a Sonar-coloured accent. The brief pins the world: SonarQube's Echoes design system. Default Streamlit chrome (red accent, Source Sans, emoji metrics) is the arrangement it refuses.

OWN-WORLD: Echoes tokens. Inter for all UI text, Ubuntu Mono for code and file names. Indigo #5d6cd0 accent; cool slate text (#1d212f / #3e4357 / #637192); #e1e6f3 hairlines; #eff2f9 table headers; 4px control radius, 8px panels. State colours come from Echoes (danger #d92d20, warning #f5b840, success #75a92c, info #316c92). Light theme, plus Echoes dark (page #2a2f40, sidebar #1d212f, accent #9fa9ed), following the OS.

STORY: The assessor recognises the SonarQube environment they work in every day, reads the level the way they read a project rating, sees straight away whether Jev's score agrees with it, and goes straight to the items flagged for review.

FIRST VIEWPORT: The left sidebar works like SonarQube's sidebar navigation (#fcfcfd, a hairline border, a "Maturity Assessment" product name, the customer select). The main column opens with a SonarQube-style project header: customer name at heading-xlarge, assessor and folder as subtle metadata. Under it, underline project tabs. Review leads with an overview strip: a square rating badge for the criteria level (5→A green … 1→E red, showing the level number and the LEVELS name), a second badge for Jev's score, and the recommendation counts. The primary action is an indigo button at the end of each tab's flow.

FORM: brief-pinned world (SonarQube Echoes), Operate shell. Signature move: the maturity level drawn as a SonarQube rating badge. seed: skipped (the user pinned the world to SonarQube; no roll was run)

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
