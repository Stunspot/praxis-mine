# Accessibility Review Receipt

**REVIEW_KIND:** ACCESSIBILITY
**REVIEWED_CANDIDATE:** 652cf4cddf72ef9f616fe02720dade53f9dac270
**DOCUMENTATION_FINGERPRINT:** 3156678139da35ba703ed716ebf81c3ba7f1bc30e6850baaef28236b6f6b235b

## EVIDENCE_BY_CRITERION

| Criterion | Evidence |
|-----------|----------|
| **Information Architecture** | The layout file defines a clear root structure: `<header>`, `<nav aria-label="Primary navigation">`, `<main id="main-content">`, and `<footer>`; internal routing uses Jekyll's `relative_url` ensuring stable links. All 27 declared documents exist, manifest paths are unique, and relative links resolve without conflict. |
| **Headings** | Each primary page (README.md, docs/index.md, etc.) begins with an H1 following a centered hero image. Subsequent sections use appropriate H2–H4 levels in the source content, maintaining a logical hierarchy with no skipped heading levels or duplicate H1s. |
| **Link Purpose** | Navigation links contain clear, descriptive text (“Start”, “Install”, “First mine”, “Workflows”, etc.). The brand link text reads “Collaborative Dynamics Praxis Mine,” and the skip link’s visible label is “Skip to content.” All external references have identifiable anchor text. |
| **Alt Text** | - README hero alt: *“Praxis Mine assay diagram: a gold capability seam passes through a cyan gate and emerges as one clean capability delta.”* <br> - Pages hero alt: *“Praxis Mine disposition board showing pilot, quarry, adapt, monitor, and reject as five evidence‑backed outcomes.”*<br> - Social card alt: *“Praxis Mine social card: Praxis Mine, Mine outside AI systems, Keep only the capability delta.”* <br> No image in the layout has a missing or empty alt attribute. |
| **Landmarks** | The markup uses semantic landmarks: `<header>` (site header), `<nav aria-label="Primary navigation">` (navigation landmark), `<main id="main-content">` (primary content), and `<footer>` (footer landmark). These provide screen‑reader users with quick access to page sections. |
| **Skip Navigation** | The skip link (`<a class="skip-link" href="#main-content">Skip to content</a>`) is positioned off‑screen until it receives focus; the `:focus` rule brings it into view via a CSS transform, making keyboard users able to bypass repetitive navigation. |
| **Focus Visibility** | Global `a:focus-visible` rules supply a 3 px solid gold outline with an offset and border‑radius for any focused link. Navigation links receive additional hover/focus styles that preserve the visible focus indicator. |
| **Contrast** | CSS contrast ratios, as measured in the static evidence, are all well above WCAG AA: <br> – body 18.97:1 <br> – muted 11.85:1 <br> – dim 6.70:1 <br> – cyan 11.85:1 <br> – cyan‑soft 15.26:1 <br> – gold 11.96:1 <br> – button text on cyan 11.32:1 <br> – button text on white 19.31:1 <br> – blockquote 17.67:1 |
| **Table & Code Reflow** | Tables and `<pre>` blocks are styled with `display:block`, `width:100%`, and `overflow-x:auto` to allow horizontal scrolling on narrow viewports, preventing layout breakage. |
| **Responsive Rules** | The stylesheet defines a responsive breakpoint at `max-width:760px`. At this width, the shell width is reduced, header flex direction switches to column, navigation justification changes, content panel padding decreases, hero border radius adapts, grid columns collapse to one, and the footer becomes stacked. |
| **Reduced Motion Handling** | The media query `@media (prefers-reduced-motion: reduce)` sets `scroll-behavior:auto` and turns off all CSS transitions for a motion‑reduction compliant experience. |
| **Recovery Routes & Cognitive Clarity** | Static documentation follows consistent layout, heading hierarchy, and minimal jargon. There are no interactive elements that require dynamic recovery; all navigation and content presentation remain clear in both desktop and mobile contexts. |
| **Image Role Suitability** | All images provide descriptive alt text and are not used purely decoratively. No image has a role of “presentation” or lacks an accessible name. |

## MATERIAL_FINDINGS

| Severity | File | Defect | Repair |
|----------|------|--------|--------|
| None | – | – | – |

> **No unresolved material accessibility findings were identified.**

## UNEXECUTED_CONDITIONS
- browser interaction
- keyboard traversal
- screen reader
- zoom
- localization
- representative-user testing
- assistive technology execution

*All listed conditions remain unexecuted; the review relied solely on static source inspection and manual pixel observations.*

## DISPOSITION

**REVIEW_PASS**

The documentation meets all examined accessibility criteria with no outstanding issues.