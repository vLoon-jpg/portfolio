# PRD — vLoon Portfolio Redesign v2

**Owner:** Levy (vLoon) · **Author:** Claude (orchestrator) · **Date:** 2026-07-13
**Deliverable:** A redesigned `index.html` (single file, no build step) that keeps 100% of current content and functionality.

---

## 1. Background

The current portfolio (`index.html`, ~2,000 lines) is a dark, orange-accented one-pager with a
standout feature: an interactive Kali-style terminal with picoCTF challenges, tmux split panes,
and a nano editor. The visual shell around it, however, reads as a generic "AI dark portfolio":
default system font, rounded glass cards, pill tags, centered glow hero — patterns seen on
thousands of sites.

**Goal:** Make the visual design as distinctive as the terminal feature. The terminal is the
soul of this site — the redesign should make the whole page feel like it belongs to the same
world as that terminal.

## 2. Objectives

1. A distinctive, cohesive visual identity ("mission-control / terminal-brutalist") that a
   visitor remembers.
2. Zero functionality loss — every interactive feature works exactly as before.
3. Zero pipeline breakage — `update.py` must still regenerate the Featured Projects section
   without visual damage.
4. Stays a single static `index.html` deployable anywhere (GitHub Pages etc.).

## 3. Non-goals

- No framework migration (no React/Vite/Tailwind build step).
- No content rewrite — all copy, projects, links, and the CTF challenges stay as-is.
- No changes to `update.py`, `projects_config.json`, or the scheduled-task scripts.
- No light mode.

## 4. Hard constraints (breaking any of these fails review)

### 4.1 update.py contract — CRITICAL
`update.py` (scheduled via `auto-update.ps1`) replaces everything between
`<!-- FEATURED PROJECTS START -->` and `<!-- FEATURED PROJECTS END -->` with hardcoded HTML:

```html
<section id="featured-projects" class="section">
  <div class="container">
    <h2>Featured Projects</h2>
    <p class="section-sub">Things I've built — … (N projects)</p>
    <div class="projects-list">
      <div class="project-card" onclick="…">
        <div class="project-header"><h3>{emoji} {title}</h3><span class="project-link-icon">↗</span></div>
        <p>{description}</p>
        <div class="project-tags"><span class="tag">…</span></div>
      </div>
      …
```

Therefore the redesign **must style these exact class names and this exact DOM shape via CSS
only**. The markers, section id, and inner structure may not be renamed or restructured. Any
JS enhancement of project cards (e.g. entrance animations) must select these classes and
tolerate the section being regenerated. Verify post-redesign with
`python update.py --dry-run` mentally: the generated markup must look correct under the new CSS.

### 4.2 Preserve all functionality
- The interactive terminal (`#termWindow`, all `term-*` classes/ids, panes, tmux split, nano,
  CTF commands, chips) — keep the JS untouched unless a change is provably cosmetic. The
  terminal's own look may be polished (title bar, colors, font) but every command must still work.
- Mobile hamburger nav, smooth scrolling, anchor links (`#about`, `#skills`,
  `#featured-projects`, `#projects`, `#contact`).
- Rotating hero motto (`#heroMotto`), anime.js entrance animations (may be redesigned but the
  anime.js v4 CDN bridge in `<head>` stays functional).
- All meta/OG tags, favicon, and the footer credit line.

### 4.3 Technical
- Single file, inline CSS/JS. External deps allowed only from CDNs already reachable
  (jsdelivr, Google Fonts).
- Responsive from 360px to 1440px+. No horizontal scroll on mobile.
- `prefers-reduced-motion` respected for new animations.
- Lighthouse-sane: no multi-MB assets, no layout thrash.

## 5. Design direction — "MISSION CONTROL"

A hacker's operations console, not a corporate portfolio. Think: declassified terminal
readout, Kali desktop, cyberpunk ops dashboard — executed with restraint and typographic rigor.

### 5.1 Identity
- **Keep the brand:** near-black background, **orange `#FF6B01`** accent. This is vLoon's color.
  Add a secondary phosphor-green `#33FF66` (terminal green) used *sparingly* — prompt
  glyphs, status dots, terminal text — never as a competing accent.
- **Typography (the biggest change):**
  - Display/headings: a characterful mono or techno grotesque — `"JetBrains Mono"` (Google
    Fonts) for headings AND UI labels. Body: `"Inter"` or keep system sans for readability.
  - Headings styled like terminal output: e.g. section titles rendered as
    `┌─[ 01 · ABOUT ]` or `> about_me` with the number/glyph in orange, title in white.
  - Uppercase micro-labels with wide letter-spacing for metadata.
- **Shapes:** sharp corners (0–4px radius max) everywhere. Replace pill tags with square-bracket
  mono tags: `[Java]` `[Fabric]` — bordered, not filled.
- **Texture & structure:** keep the noise overlay (it's good). Add a faint fixed background
  grid (1px lines, ~2–3% opacity) and thin `1px` orange rules/frames around sections — like a
  blueprint or HUD. Corner tick marks (`+`) at section frame corners are encouraged.
- **Status line:** a persistent thin top-of-nav or bottom-of-viewport strip in mono:
  `vloon@portfolio ~ [ONLINE] · Amlapura, Bali · UTC+8` with a blinking cursor. This is the
  signature element.

### 5.2 Section-by-section
- **Nav:** keep fixed glass nav but square it off; logo becomes `[Lv]` or `vloon@:~$` in mono;
  links get mono uppercase micro-labels with `//` or `_` prefixes on hover.
- **Hero:** left-aligned. Replace the pulsing pill badge with a mono boot-sequence line
  (`> initializing vloon.dev … OK`). Name stays huge (clamp ~5rem) but in the mono/display
  face with the accent on `(vLoon)`. Typed-out motto with a real blinking block cursor `█`
  instead of fading italic text. Buttons become bracketed mono buttons: `[ SEE MY WORK → ]`,
  `[ CONTACT ]`. Optional: faint ASCII or coordinates (`-8.45°S 115.60°E`) as hero garnish.
- **About:** keep two-column grid. Quick Facts card becomes a `key: value` readout styled like
  a config file / neofetch output (mono, orange keys, no bullets).
- **Skills:** replace the 6 centered emoji cards with a denser HUD grid — each cell: mono
  skill name, one-line description, a subtle `▮▮▮▯` level bar or hex-ish index (`0x01`), hover
  reveals the external link. Sharp borders, hover = orange border + slight glow. Emojis may go.
- **Featured Projects (update.py-owned DOM):** restyle `.project-card` as ledger rows /
  index entries: mono index number (via CSS counters — DOM can't change), title, description,
  bracket tags, `↗` in a framed square at right. Hover: orange left rule or frame + background
  shift. Keep the vertical list layout (it works with regeneration).
- **CTF Terminal section:** this becomes the centerpiece. Frame it like a real window on the
  Kali desktop: keep functionality, upgrade chrome (mono title bar, squared corners, orange
  focus ring when active). Section intro copy styled as a mission briefing. The `term-chips`
  become mono command chips: `$ tmux`, `$ neofetch`.
- **Contact:** three ledger-style rows or framed cells with mono handles; hover = orange frame.
- **Footer:** mono, include a fake exit line: `process exited with code 0 · © 2026 Levy (vLoon)`.

### 5.3 Motion
- Keep anime.js. Entrance: sections/cards get short staggered fade-up (≤500ms) on scroll.
- Hero: boot-sequence lines type in on load; motto types/deletes with block cursor.
- Hover states are instant (≤150ms). No parallax, no scroll-jacking, no infinite marquees.
- Everything gated behind `prefers-reduced-motion`.

### 5.4 Anti-goals (banned)
Generic glassmorphism cards, purple/blue gradient text, rounded-2xl pills, emoji as primary
iconography (outside terminal content), centered-everything layouts, cookie-cutter "gradient
blob" backgrounds.

## 6. Acceptance criteria

1. Page renders correctly at 360px, 768px, 1280px with no horizontal overflow.
2. All nav anchors scroll to the right sections; hamburger works on mobile.
3. Terminal: `help`, `neofetch`, `tmux` (split), `ls /opt/ctf`, nano open/exit all work.
4. Hero motto rotation/typing works; no JS console errors.
5. The Featured Projects section between the markers, if regenerated by `update.py`, would
   render correctly under the new CSS (class names and DOM shape untouched).
6. Design review: the page no longer reads as a template; the "Mission Control" language is
   applied consistently in every section.
7. Original design preserved at `index.backup-v1.html`.

## 7. Rollout

1. Back up current file → `index.backup-v1.html`.
2. Implement redesign in `index.html`.
3. Orchestrator verifies in browser (desktop + mobile widths, terminal smoke test).
4. Levy reviews; iterate on feedback.
