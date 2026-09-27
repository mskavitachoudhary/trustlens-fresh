# Institutional & Editorial Redesign — Design Specification

**Date:** 2026-09-27  
**Status:** Approved  
**Author:** Principal Frontend Architect & Staff Product Designer  

---

## 1. Executive Summary & Objective

TrustLens is transitioning from a generic "AI-generated" aesthetic (oversaturated rainbow gradients, neon badges, heavy glassmorphism blurs, floating aurora orbs) to an **institutional-grade, editorial web interface** reminiscent of Linear, Stripe Press, Vercel, and modern financial security infrastructure.

The core goal is to establish immediate authority, trust, and clarity through:
1. **Monochrome Dominance (Strict 2-Color Foundation):** Canvas and surface neutrals plus a single intentional accent (`#0f172a` in light mode, `#f4f4f5` in dark mode).
2. **Typography-First Structure:** Hierarchy achieved via disciplined scale, negative letter tracking (`-0.025em` to `-0.035em`), tabular numerals, and muted micro-labels.
3. **Restraint Over Decoration:** Elimination of all mesh gradients, floating orbs, particle canvases, and neon glow. Surfaces are separated by crisp 1px borders (`border-subtle`).
4. **Light & Dark Theme Parity:** Native theme switching (`light` | `dark` | `system`) with anti-FOUC initialization and complete semantic parity.
5. **Functional Semantic Signals:** Muted emerald, amber, and crimson reserved exclusively for verification results, status chips, and score meters.

---

## 2. Design System Tokens (CSS Variables)

```css
:root {
  /* LIGHT THEME (Editorial Paper & Slate) */
  --bg-canvas: #fbfbfb;
  --bg-surface: #ffffff;
  --bg-surface-elevated: #f4f4f5;

  --text-primary: #111827;
  --text-secondary: #4b5563;
  --text-muted: #9ca3af;

  --border-subtle: #e5e7eb;
  --border-strong: #d1d5db;

  /* Single Intentional Accent (Obsidian ink) */
  --accent: #0f172a;
  --accent-contrast: #ffffff;
  --accent-hover: #1e293b;
  --accent-focus: rgba(15, 23, 42, 0.15);

  /* Functional Semantic Signals (Restrained & Muted) */
  --signal-safe: #047857;          /* Forest emerald */
  --signal-safe-bg: #ecfdf5;
  --signal-safe-border: #a7f3d0;
  --signal-warning: #b45309;       /* Muted amber */
  --signal-warning-bg: #fffbeb;
  --signal-warning-border: #fde68a;
  --signal-danger: #b91c1c;        /* Deep crimson */
  --signal-danger-bg: #fef2f2;
  --signal-danger-border: #fecaca;

  /* Gauge track & controls */
  --gauge-track: #e5e7eb;
  --bg-input: #ffffff;

  /* Navigation & Chrome */
  --nav-bg: rgba(251, 251, 251, 0.88);
  --nav-border: var(--border-subtle);

  /* Geometry & Shadows */
  --radius-xs: 4px;
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 14px;
  --shadow-subtle: 0 1px 2px 0 rgba(0, 0, 0, 0.04);
  --shadow-card: 0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px -1px rgba(0, 0, 0, 0.05);
}

[data-theme='dark'] {
  /* DARK THEME (Refined Charcoal & Ink) */
  --bg-canvas: #09090b;
  --bg-surface: #121215;
  --bg-surface-elevated: #18181b;

  --text-primary: #f4f4f5;
  --text-secondary: #a1a1aa;
  --text-muted: #71717a;

  --border-subtle: #27272a;
  --border-strong: #3f3f46;

  /* Accent inversion for high legibility */
  --accent: #f4f4f5;
  --accent-contrast: #09090b;
  --accent-hover: #e4e4e7;
  --accent-focus: rgba(244, 244, 245, 0.2);

  /* Functional Semantic Signals (Deep & Understated) */
  --signal-safe: #34d399;
  --signal-safe-bg: rgba(16, 185, 129, 0.10);
  --signal-safe-border: rgba(16, 185, 129, 0.22);
  --signal-warning: #fbbf24;
  --signal-warning-bg: rgba(245, 158, 11, 0.10);
  --signal-warning-border: rgba(245, 158, 11, 0.22);
  --signal-danger: #f87171;
  --signal-danger-bg: rgba(239, 68, 68, 0.10);
  --signal-danger-border: rgba(239, 68, 68, 0.22);

  /* Gauge track & controls */
  --gauge-track: #27272a;
  --bg-input: #121215;

  /* Navigation & Chrome */
  --nav-bg: rgba(9, 9, 11, 0.88);
  --nav-border: var(--border-subtle);

  --shadow-subtle: 0 1px 2px 0 rgba(0, 0, 0, 0.4);
  --shadow-card: 0 1px 3px 0 rgba(0, 0, 0, 0.5);
}
```

---

## 3. Structural & Architectural Layout

### 3.1 Background & Surface Layout
- Remove `.bg-aurora`, `.bg-subtle-grid`, and particle canvases completely. The background is a clean, uniform `--bg-canvas`.
- Cards (`.card-trust`, `.glass`, `.glass-soft`) become flat, opaque panels:
  - `background: var(--bg-surface);`
  - `border: 1px solid var(--border-subtle);`
  - `border-radius: var(--radius-md);`
  - `box-shadow: var(--shadow-card);`
- Hover state: subtle border shift to `--border-strong` and negligible elevation; no 3D tilt, no neon blur.

### 3.2 Typography & Editorial Scale
- Global font stack: `-apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", Roboto, sans-serif`.
- Hero headings: `font-size: clamp(2.4rem, 4.8vw, 3.5rem); font-weight: 600; letter-spacing: -0.035em; line-height: 1.12; color: var(--text-primary);`.
- Section titles: `font-size: 1.75rem; font-weight: 600; letter-spacing: -0.025em; color: var(--text-primary);`.
- Section eyebrow/kicker: `font-size: 0.72rem; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: var(--text-muted);`.
- Data numerals: `font-variant-numeric: tabular-nums; letter-spacing: -0.02em;`.

### 3.3 Buttons & Actions
- **Primary CTA (`.btn-trust`, `.btn-primary`):**
  - High-contrast solid monochrome pill or rounded rectangle.
  - `background: var(--accent); color: var(--accent-contrast); border: 1px solid var(--accent);`
  - Hover: `background: var(--accent-hover);`
- **Secondary Action (`.btn-ghost`, `.btn-outline`):**
  - Crisp outline button with `background: transparent; color: var(--text-primary); border: 1px solid var(--border-strong);`
  - Hover: `background: var(--bg-surface-elevated);`

### 3.4 Gauge & Metrics System
- Meter tracks use `--gauge-track` (crisp 1px border contrast with background).
- Progress arc uses `--signal-safe`, `--signal-warning`, or `--signal-danger`.
- Inner circle background is flat `var(--bg-surface)`.
- Center numeral is tabular, bold monochrome (`var(--text-primary)`).
- Subtitle is clean uppercase micro-typography (`font-size: 0.7rem; letter-spacing: 0.12em; color: var(--text-muted);`).
- Containers enforce `aspect-ratio: 1 / 1; flex-shrink: 0;` to guarantee circular rendering.

---

## 4. Template-by-Template Architecture

1. **`templates/base.html`:**
   - Institutional navbar pinned with hairline bottom border (`border-bottom: 1px solid var(--nav-border)`).
   - Minimalist brand mark (vector shield-lens icon in neutral frame).
   - Clean theme toggle button (monochrome sun/moon icon).
   - Unified 8-scanner dropdown menu with clean 1.5px stroke icons, high-contrast labels, and subtle descriptions.
   - Minimal editorial footer with clean columns, hairline top border, and system status indicator.

2. **`templates/index.html`:**
   - Hero section: Monochrome editorial layout. Headline: "Verify before you trust." with crisp subhead.
   - Primary solid CTA ("Scan a Website") + secondary outline CTA ("Create Free Account").
   - Live demo card: Crisp verification preview with circular gauge and clear check breakdown.
   - 8 Verification Engines Grid: 4x2 responsive layout with uniform card heights, subtle 1px border lines, and clean vector icons.
   - "Why TrustLens" institutional feature grid and minimal final CTA banner.

3. **Scanner Templates (`website_scanner`, `email_scanner`, `job_checker`, etc.):**
   - Clean shell layout with breadcrumb / eyebrow kicker.
   - Uniform input containers with `--bg-input`, crisp 1px borders, and clear focus states.
   - Minimal file drop zones with dashed border and clean icon feedback.
   - Results panel: Crisp check-by-check ledger tables with hairline row dividers and semantic status chips.

4. **Dashboard & Scam Reports (`templates/reports/`, `templates/admin/`):**
   - Flat tabular data presentation with monospace identifiers and clean pagination.
   - Chart.js canvases styled to respect the monochrome palette and theme tokens.

---

## 5. Verification & Safety Safeguards

1. **DOM ID & Contract Preservation:**
   - Input element IDs (`url`, `email_text`, `job_text`, `chat_image`, `qr_image`, `payment_image`, `ingredient_input`, `claim_text`, etc.) will NOT be changed.
   - Form submission handlers, API routes, and CSRF token protections remain untouched.
2. **Automated Testing:**
   - All Python test suites in `tests/` must pass 100%.
3. **Visual Verification:**
   - Headless Chrome verification in both light and dark themes to confirm 0 layout breaks and crisp rendering.
