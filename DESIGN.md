---
name: Maturity Assessment
description: A local SonarQube-Echoes page where one assessor goes from evidence to a sendable maturity report.
colors:
  primary: "#5d6cd0"
  primary-weak: "#e8ebff"
  on-primary: "#ffffff"
  primary-dark: "#9fa9ed"
  primary-weak-dark: "#5d6cd04d"
  text-strong: "#1d212f"
  text-default: "#3e4357"
  text-subtle: "#637192"
  hairline: "#e1e6f3"
  border-bold: "#c5cddf"
  surface: "#ffffff"
  surface-secondary: "#eff2f9"
  sidebar: "#fcfcfd"
  dark-page: "#2a2f40"
  dark-surface: "#3e4357"
  dark-sidebar: "#1d212f"
  dark-text-strong: "#fcfcfd"
  dark-text-default: "#e1e6f3"
  dark-text-subtle: "#c5cddf"
  dark-border: "#637192"
  success-text: "#537c17"
  warning-text: "#8c5e1e"
  danger-text: "#b42318"
  success-text-dark: "#c4ea9e"
  warning-text-dark: "#fadc79"
  danger-text-dark: "#fda29b"
  rating-a-bg: "#d1fadf"
  rating-a-text: "#054f31"
  rating-a-border: "#12b76a"
  rating-b-bg: "#d4f2b7"
  rating-b-text: "#054f16"
  rating-b-border: "#9dcb6b"
  rating-c-bg: "#fce9a3"
  rating-c-text: "#66400f"
  rating-c-border: "#f5b840"
  rating-d-bg: "#ffd6af"
  rating-d-text: "#7a2e0e"
  rating-d-border: "#fd7122"
  rating-e-bg: "#fecdca"
  rating-e-text: "#5d1d13"
  rating-e-border: "#f04438"
  rating-a-bg-dark: "#027a48"
  rating-a-text-dark: "#f6fef9"
  rating-a-border-dark: "#32d583"
  rating-b-bg-dark: "#537c17"
  rating-b-text-dark: "#f3f8ef"
  rating-b-border-dark: "#b3dd86"
  rating-c-bg-dark: "#8c5e1e"
  rating-c-text-dark: "#fcf5e4"
  rating-c-border-dark: "#fadc79"
  rating-d-bg-dark: "#b54708"
  rating-d-text-dark: "#fff0eb"
  rating-d-border-dark: "#f75f09"
  rating-e-bg-dark: "#b42318"
  rating-e-text-dark: "#fef3f2"
  rating-e-border-dark: "#fda29b"
typography:
  headline:
    fontFamily: "Inter, ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif"
    fontSize: "1.5rem"
    fontWeight: 600
    lineHeight: "2.25rem"
  title:
    fontFamily: "Inter, ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif"
    fontSize: "1rem"
    fontWeight: 600
    lineHeight: "1.5rem"
  body:
    fontFamily: "Inter, ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: "1.25rem"
  tab:
    fontFamily: "Inter, ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 600
  label:
    fontFamily: "Inter, ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif"
    fontSize: "0.75rem"
    fontWeight: 600
    lineHeight: "1rem"
  rating:
    fontFamily: "Inter, ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif"
    fontSize: "1.25rem"
    fontWeight: 700
    lineHeight: 1
    fontFeature: "tnum"
  mono:
    fontFamily: "'Ubuntu Mono', ui-monospace, SFMono-Regular, Menlo, monospace"
    fontSize: "0.9375rem"
    fontWeight: 400
rounded:
  control: "4px"
  panel: "8px"
spacing:
  xs: "4px"
  sm: "12px"
  md: "16px"
  lg: "20px"
  xl: "24px"
  page-top: "64px"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    typography: "{typography.body}"
    rounded: "{rounded.control}"
  button-primary-dark:
    backgroundColor: "{colors.primary-dark}"
    textColor: "{colors.dark-page}"
    typography: "{typography.body}"
    rounded: "{rounded.control}"
  button-secondary:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text-default}"
    typography: "{typography.body}"
    rounded: "{rounded.control}"
  tab:
    textColor: "{colors.text-subtle}"
    typography: "{typography.tab}"
  tab-active:
    textColor: "{colors.text-strong}"
    typography: "{typography.tab}"
  rating-badge-a:
    backgroundColor: "{colors.rating-a-bg}"
    textColor: "{colors.rating-a-text}"
    typography: "{typography.rating}"
    rounded: "{rounded.panel}"
    size: "40px"
  rating-badge-e:
    backgroundColor: "{colors.rating-e-bg}"
    textColor: "{colors.rating-e-text}"
    typography: "{typography.rating}"
    rounded: "{rounded.panel}"
    size: "40px"
  overview-cell:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.panel}"
    padding: "16px 20px"
  input:
    backgroundColor: "{colors.surface-secondary}"
    textColor: "{colors.text-default}"
    typography: "{typography.body}"
    rounded: "{rounded.control}"
---

# Design System: Maturity Assessment

## Overview

**Creative North Star: "A Page Inside SonarQube"**

The tool is meant to read as one more page of SonarQube Server, built on Sonar's Echoes tokens, rather than as a Streamlit app with a Sonar-coloured accent. The assessor already works in SonarQube every day. The sidebar, the project header, the underline tabs and the rating badge all come from that environment, so nothing has to be learned. The Streamlit defaults (red accent, Source Sans, emoji metrics) are replaced, not tinted.

It is an Operate surface: dense, calm and flat. Cool slate text sits on white (or on the Echoes dark slate). Hairline borders separate panels, and the only saturated colours are the single indigo action per tab and the A–E rating colours. The signature is the maturity level drawn as a SonarQube rating badge. Level 5 maps to A (green) and level 1 to E (red), and the badge shows the level digit, so a reading of the level works exactly like a reading of a project's reliability rating.

Light and dark follow the OS setting by default; the app menu (⋮, top right) switches between System, Light and Dark. Every custom token has a light and a dark value, emitted as CSS `light-dark()` variables on `.stApp` so the custom pieces switch with the menu without a rerun, and the dark values are chosen for contrast, not by inverting the light ones.

**Key Characteristics:**
- Echoes tokens throughout: Inter for UI text, Ubuntu Mono for code and file paths, both self-hosted.
- One indigo primary action per tab, placed at the end of that tab's flow.
- The rating badge (level digit in a 40px square, A–E colour) is the only decorative colour.
- Flat surfaces separated by 1px hairlines. 4px corners on controls, 8px on panels.
- Light and dark follow the OS unless the app menu picks one, and each has its own tuned token set.

## Colors

A cool slate neutral scale with one indigo accent, plus Echoes state and rating colours that appear only when they carry meaning.

### Primary
- **Echoes Indigo** (primary; primary-dark in dark mode): primary buttons, links, the active tab underline, progress fills and toggles. Indigo appears only on things you act on or on progress. It is never used for decoration.
- **Indigo Wash** (primary-weak; primary-weak-dark): text selection highlight.
- **On-Indigo** (on-primary in light mode; dark-page in dark mode): text on primary buttons. In dark mode, primary buttons use the dark page slate (#2a2f40) for their text, not white, because white on the light dark-mode indigo fails contrast.

### Neutral
- **Ink Slate** (text-strong; dark-text-strong): customer name, section headings, active tabs, values in the overview strip, table header text.
- **Body Slate** (text-default; dark-text-default): running text and inline code in metadata.
- **Muted Slate** (text-subtle; dark-text-subtle): metadata, captions, inactive tabs, overview cell labels and notes.
- **Hairline** (hairline; dark-surface in dark mode): header rule, tab rail, panel and form borders, overview cell dividers, dataframe grid.
- **Control Border** (border-bold; dark-border): input and secondary-button strokes, and the scrollbar thumb.
- **Paper / Cloud / Sidebar White** (surface, surface-secondary, sidebar): the page, then table headers, code and input fills, then the sidebar.
- **Echoes Dark Slates** (dark-page, dark-surface, dark-sidebar): the dark page, the dark secondary surface, and the sidebar, which sits deeper than the page.

### State
- **Success / Warning / Danger text** (success-text, warning-text, danger-text, plus the -dark variants): text-tier Echoes tones used only for inline status words in the overview strip. Streamlit alerts take their colours from the full Echoes red, orange, yellow, green, blue, violet and gray sets in `.streamlit/config.toml`.

### Rating
- **A–E rating triplets** (rating-{a..e}-bg / -text / -border, plus the -dark variants): used only by the rating badge. Each triplet is a pale fill with a darker text colour and a saturated border. In dark mode the fill is the deep tone and the text is near-white. The dark B and C fills are #537c17 and #8c5e1e, set deliberately for text contrast.

### Named Rules
**The One Indigo Rule.** Each tab has at most one indigo primary button, placed at the end of its flow. Every other action is secondary.

**The Warning-Not-Danger Rule.** When Jev's score differs from the criteria level, and when items are flagged "to review", the note uses the warning colour. A disagreement asks the assessor to check something. It is not an error.

**The Rating-Only Colour Rule.** Green-through-red fills appear only in the rating badge. They never go on tags, cells or chart chrome in the UI.

## Typography

**Display Font:** none. The largest type is the headline.
**Body Font:** Inter (with ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto), self-hosted at weights 400, 500, 600 and 700.
**Label/Mono Font:** Ubuntu Mono (with ui-monospace, SFMono-Regular, Menlo), self-hosted at 400 and 700.

**Character:** This is SonarQube's own pairing. Inter does all the interface work in sentence case. Ubuntu Mono marks anything that is literally a path, file name or key.

### Hierarchy
- **Headline** (600, 1.5rem / 2.25rem): the customer name in the page header, and the large number in the overview strip.
- **Title** (600, 1rem / 1.5rem): section headings within a tab (Add evidence, Recommendations, Download) and the sidebar product name. Expander summaries use 600 at body size.
- **Body** (400, 0.875rem / 1.25rem; base font size 14px): all running text, metadata, captions, overview notes and values in the controls.
- **Tab** (600, 0.875rem): project tabs.
- **Label** (600, 0.75rem / 1rem, sentence case): overview cell labels.
- **Rating** (700, 1.25rem, line-height 1, tabular figures): the level digit in the badge.
- **Mono** (Ubuntu Mono 400, 0.9375rem; 1.05em when inline in body text): file names, folder paths, customer.json keys.

### Named Rules
**The Tabular Numbers Rule.** Metric values, progress bars, rating digits and counts use tabular figures so columns of numbers line up.

**The Sentence Case Rule.** Labels, tabs and headings are written in sentence case, as in Echoes. Do not use uppercase or letter-spaced labels.

## Layout

A SonarQube shell: a left sidebar on #fcfcfd (#1d212f in dark mode) with a hairline right border, holding the product name, the customer select, the new-customer expander and the data notice. The main column is capped at 1280px with 4rem of top padding.

From top to bottom, the main column has:
- a project header: the customer name, then a meta line ("Assessor: [name] · `customers/example_customer`"), then a hairline rule with 1rem padding below it;
- underline tabs (1 · Evidence, 2 · Run, 3 · Review & download, Charts) with 1.5rem between tabs and 1.5rem of padding above each panel.

Inside a tab, content flows top to bottom and ends at the primary action. Paired fields and uploaders sit in two-column rows. The Charts form uses three columns.

The spacing rhythm uses 4px, 12px, 16px, 20px and 24px steps. At 720px and below, the three-cell overview strip stacks into a single column, and the cell dividers move from the left edge to the top edge.

### Named Rules
**The Flow-Order Rule.** Tabs follow the work: Evidence, then Run, then Review & download, with Charts as an unnumbered annex. Inside each tab the primary action comes last.

## Elevation & Depth

Flat. Depth comes from tonal layering (sidebar, page, secondary surface) and 1px hairlines. The build adds no box-shadows of its own. The only shadows are Streamlit's native ones on popovers and select menus, which match Echoes' floating-layer treatment.

### Named Rules
**The Hairline-Not-Shadow Rule.** Group content with a 1px hairline border and an 8px panel radius. Never use a shadow for grouping.

## Shapes

Gently rounded and rectilinear. Buttons, inputs and the base widget radius are 4px. Panels (forms, expanders, the overview strip) and the rating badge are 8px. The rating badge is a 40px square, never a circle. Widget borders and the sidebar border are always visible.

## Components

### Buttons
- **Shape:** gently rounded (4px).
- **Primary:** Echoes Indigo fill. Text is white in light mode and #2a2f40 in dark mode. There is one per tab, at the end of the flow:
  - Evidence: Save files.
  - Run: "Rebuild report from cached answers" when a cache exists. With no cache, "Run assessment with Jev" is primary instead.
  - Review: the Word report (.docx) download is primary. "Save choices and rebuild report" becomes primary, and enabled, only when there are unsaved changes; otherwise it is a disabled secondary.
  - Charts: Create charts.
  - The confirm button inside the Remove-file popover is primary, because it is the only action in that popover.
- **Secondary:** surface fill, Control Border stroke, Body Slate text.
- **Disabled:** Streamlit's muted native treatment. The secondary actions Run assessment, Save choices and Rebuild show disabled when they can't apply. They are never hidden.

### Navigation (project tabs)
- Inter 600 at 0.875rem. Inactive tabs are Muted Slate. Hover and selected tabs are Ink Slate, and the selected tab has the indigo underline. The tab rail is a Hairline. Tab labels carry their step number ("1 · Evidence"). The annex tab has no number.

### Cards / Containers (forms, expanders, overview strip)
- **Corner Style:** 8px.
- **Background:** the page surface.
- **Shadow Strategy:** none (see Elevation & Depth).
- **Border:** 1px Hairline. Expander summaries are 600 weight.
- **Internal Padding:** 16px by 20px in overview cells.

### Inputs / Fields
- **Style:** Streamlit native with Echoes colours: 4px radius, Control Border stroke, visible widget borders. Fields are labelled in sentence case. Placeholders are neutral, invented examples (a generic company name, "2026-05").
- **Focus:** indigo focus ring (via primaryColor).
- **Data editor:** Cloud header fill with Ink Slate header text and a Hairline grid. Only the Include column is editable. Probabilities show as indigo progress columns formatted as percentages.

### Overview Strip (Review)
A three-cell bordered strip at the top of Review:
1. **Maturity level (criteria):** a rating badge, then "Level N", then the level name.
2. **Jev's overall score:** a rating badge, then "Level N" and the level name, then an agreement note. The note is success-coloured when the score agrees with the criteria level and warning-coloured when it differs.
3. **Recommendations:** the included count at headline size, with "included" as a note beside it, then "N to review" in warning colour, or "none to review".

### Rating Badge (signature)
A 40px square with an 8px radius and a 1px border, showing the level digit in Inter 700 at 1.25rem with tabular figures. The colour comes from level → rating: 5→A, 4→B, 3→C, 2→D, 1→E, using the triplet for the current theme. The badge is aria-hidden, so "Level N" and the level name must always appear in text next to it.

### Review List
Flagged "To review" items always sort first. The "Only show items to review" toggle is on by default whenever any item is flagged. The flag is the word "To review" in its own column, not an icon.

## Do's and Don'ts

### Do:
- **Do** take every colour from the Echoes tokens above or from `.streamlit/config.toml`, with a light value and a dark value for each.
- **Do** keep exactly one indigo primary per tab, at the end of its flow. Promote Save to primary only when there are unsaved changes.
- **Do** show maturity levels as the rating badge (5→A … 1→E), always with "Level N" in text beside it.
- **Do** use the warning colour, not danger, for disagreements and for items to review.
- **Do** sort flagged items first and turn the review filter on by default when any item is flagged.
- **Do** set file names, paths and JSON keys in Ubuntu Mono, and set counts and metrics in tabular figures.
- **Do** use #2a2f40 text on dark-mode primary buttons, and the #537c17 / #8c5e1e dark fills for B and C badges.

### Don't:
- **Don't** reintroduce Streamlit's default chrome: red accent, Source Sans, or emoji in metrics or labels.
- **Don't** add a second indigo primary to a tab, or use indigo for decoration.
- **Don't** use the A–E rating colours anywhere except the rating badge.
- **Don't** add box-shadows for grouping. Use a hairline and an 8px radius.
- **Don't** write uppercase or letter-spaced labels, or decorative eyebrows above headings.
- **Don't** put real customer names or data into examples, placeholders or screenshots. Use neutral placeholders.
