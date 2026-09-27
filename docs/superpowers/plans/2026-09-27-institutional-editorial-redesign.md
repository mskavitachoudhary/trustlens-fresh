# Institutional & Editorial Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform TrustLens into an institutional-grade, editorial web application reminiscent of Linear, Stripe Press, and Vercel by eliminating generic AI glassmorphism/neon gradients and adopting a strict 2-color monochrome hierarchy with restrained semantic signals.

**Architecture:** A centralized CSS token architecture (`:root` / `[data-theme='dark']`) driving flat opaque surfaces, hairline 1px borders, disciplined typography (`letter-spacing: -0.025em`), and monochrome actions. Functional signals (safe/warning/dangerous) are strictly confined to verification results and score meters.

**Tech Stack:** Bootstrap 5, Jinja2, Vanilla CSS Custom Properties, Modern JavaScript (ES6+), Flask backend.

**Spec:** [docs/superpowers/specs/2026-09-27-institutional-editorial-redesign-design.md](file:///Users/dineshchoudhary/Developer/kavita/trustlens-fresh/docs/superpowers/specs/2026-09-27-institutional-editorial-redesign-design.md)

## Global Constraints

- Simple English commit messages at all times.
- Never alter scanner form input element IDs (`url`, `email_text`, `job_text`, `chat_image`, `qr_image`, `payment_image`, `ingredient_input`, `claim_text`, etc.).
- Never modify backend API routes or JSON response payloads.
- Strict 2-color foundation: canvas + surface neutrals with single accent (`#0f172a` light / `#f4f4f5` dark). No decorative multi-color gradients.
- All automated unit tests in `tests/` must pass 100%.

## Review Focus

1. **Light / Dark Theme Contrast:** Ensure light theme text has minimum 4.5:1 contrast against `#fbfbfb` / `#ffffff` and dark mode cards do not collapse into pitch black.
2. **Gauge Aspect Ratio:** Ensure circular meters never compress into ovals or eggs under any flex parent or viewport size.
3. **Form Submissions & Feedback:** Ensure loading states and error messages remain fully legible in both color schemes.
4. **Mobile Navigation:** Ensure the dropdown scanner menu and theme toggle remain accessible on small viewports (<768px).
5. **No Visual FOUC:** Ensure the anti-FOUC theme detection script in `<head>` seamlessly loads without flash of wrong theme.

---

### Task 1: Global Editorial Design System Tokens & Base Stylesheet

**Files:**
- Modify: `static/css/style.css:1-120`
- Test: `tests/test_website_scanner.py`

**Interfaces:**
- Consumes: Theme attribute on `<html>` (`data-theme="light"` / `data-theme="dark"`).
- Produces: Global CSS custom properties (`--bg-canvas`, `--bg-surface`, `--bg-surface-elevated`, `--text-primary`, `--text-secondary`, `--text-muted`, `--border-subtle`, `--border-strong`, `--accent`, `--accent-contrast`, `--signal-safe`, `--signal-warning`, `--signal-danger`, `--gauge-track`).

- [ ] **Step 1: Inspect and run test suite baseline**
Run: `.venv/bin/python -m unittest discover tests/`
Expected: 20 tests pass.

- [ ] **Step 2: Update CSS tokens and base styles in `static/css/style.css`**
Define exact requested tokens in `:root` and `[data-theme='dark']`. Replace background styling, remove `.bg-aurora` and `.bg-subtle-grid` remnants, set flat `--bg-canvas` and editorial font hierarchy.

- [ ] **Step 3: Run test suite to verify no regressions**
Run: `.venv/bin/python -m unittest discover tests/`
Expected: 20 tests pass.

- [ ] **Step 4: Commit**
```bash
git add static/css/style.css
git commit -m "update design tokens and base styles for editorial theme"
```

---

### Task 2: Global Chrome & Navigation Shell

**Files:**
- Modify: `templates/base.html:30-120`
- Modify: `static/css/style.css:120-240`
- Test: `tests/test_website_scanner.py`

**Interfaces:**
- Consumes: Base CSS tokens, `icon` Jinja macro from `templates/components/icons.html`.
- Produces: Pinned institutional navbar with hairline border, monochrome brand mark, theme toggle, and 8-scanner dropdown menu.

- [ ] **Step 1: Update navbar and footer markup in `templates/base.html`**
Set clean pinned navbar with hairline border bottom (`var(--nav-border)`). Ensure minimalist brand mark, theme toggle, and 8-scanner dropdown menu.

- [ ] **Step 2: Update navigation and chrome styles in `static/css/style.css`**
Style `.navbar-trust`, `.nav-dropdown-menu`, `.brand-mark`, and `.footer-trust` with flat neutral surfaces, subtle hover states, and zero glow.

- [ ] **Step 3: Run tests to verify template rendering**
Run: `.venv/bin/python -m unittest discover tests/`
Expected: All tests pass.

- [ ] **Step 4: Commit**
```bash
git add templates/base.html static/css/style.css
git commit -m "redesign navigation header and footer with institutional styling"
```

---

### Task 3: Editorial Homepage Transformation

**Files:**
- Modify: `templates/index.html:1-140`
- Modify: `static/css/style.css:240-360`
- Test: `tests/test_website_scanner.py`

**Interfaces:**
- Consumes: Navigation shell, iconography macro, scanner route endpoints.
- Produces: Editorial hero, monochrome CTA pair, live preview card, 4x2 verification engines grid, institutional feature grid.

- [ ] **Step 1: Update homepage markup in `templates/index.html`**
Redesign hero with tight negative tracking, headline "Verify before you trust.", solid accent CTA ("Scan a Website") and secondary outline CTA ("Create Free Account"), live preview card with circular gauge, and 8-scanner grid cards with uniform height and subtle borders.

- [ ] **Step 2: Update hero and showcase card styles in `static/css/style.css`**
Eliminate gradient text (`.text-gradient`), style flat `.card-trust` and `.tool-card` with 1px border separation and restrained hover elevation.

- [ ] **Step 3: Run tests**
Run: `.venv/bin/python -m unittest discover tests/`
Expected: All tests pass.

- [ ] **Step 4: Commit**
```bash
git add templates/index.html static/css/style.css
git commit -m "redesign homepage with editorial typography and scanner grid"
```

---

### Task 4: Scanner Form Interfaces & Drop Zones

**Files:**
- Modify: `static/css/style.css:480-620`
- Modify: `static/js/main.js:70-130`
- Test: `tests/test_email_scanner.py`, `tests/test_claim_scanner.py`, `tests/test_product_scanner.py`

**Interfaces:**
- Consumes: Scanner template form markup (`scanForm`, input IDs).
- Produces: Uniform institutional form controls (`.form-control-trust`), drag-and-drop zones (`.drop-zone`), and monochromatic action buttons.

- [ ] **Step 1: Refine form input and drop zone CSS in `static/css/style.css`**
Set flat background (`var(--bg-input)`), crisp 1px borders, subtle focus ring (`var(--accent-focus)`), and minimalist drag-over feedback.

- [ ] **Step 2: Ensure drop zone event handlers and button loading states in `static/js/main.js`**
Ensure spinner and loading labels use monochrome styles without broken layouts.

- [ ] **Step 3: Run scanner unit tests**
Run: `.venv/bin/python -m unittest discover tests/`
Expected: 20 tests pass.

- [ ] **Step 4: Commit**
```bash
git add static/css/style.css static/js/main.js
git commit -m "refine scanner form controls and drop zones"
```

---

### Task 5: Architectural Gauge & Result Cards

**Files:**
- Modify: `static/css/style.css:620-720`
- Modify: `static/js/main.js:135-210`
- Test: `tests/test_email_scanner.py`, `tests/test_product_scanner.py`

**Interfaces:**
- Consumes: Scanner result payloads (score, risk_label, checks).
- Produces: Circular score meter (enforcing aspect ratio 1:1), tabular numeral display, check-by-check ledger tables (`.chk-table`), and semantic verdict pills.

- [ ] **Step 1: Update gauge and result card CSS in `static/css/style.css`**
Enforce `aspect-ratio: 1 / 1; flex-shrink: 0;` on `.gauge-wrap` and `.gauge-ring`. Use `--gauge-track` and semantic signal tokens. Style `.chk-table` with subtle hairline dividers.

- [ ] **Step 2: Update `renderGauge` and `renderRiskGauge` in `static/js/main.js`**
Ensure scores are clamped (0-100), conic-gradient uses `--signal-safe`, `--signal-warning`, `--signal-danger`, and tabular numerals are centered with crisp typography.

- [ ] **Step 3: Run scanner tests**
Run: `.venv/bin/python -m unittest discover tests/`
Expected: 20 tests pass.

- [ ] **Step 4: Commit**
```bash
git add static/css/style.css static/js/main.js
git commit -m "redesign circular gauge and verification result cards"
```

---

### Task 6: Secondary Pages, Scam Reports & Admin Dashboard

**Files:**
- Modify: `static/css/style.css:900-1100`
- Modify: `templates/admin/dashboard.html:105-180`
- Test: `tests/test_website_scanner.py`

**Interfaces:**
- Consumes: Admin analytics and scam reports templates.
- Produces: Flat tabular ledger layout, monospace ID pills, and theme-adaptive Chart.js charts.

- [ ] **Step 1: Style tables, pagination, and chips in `static/css/style.css`**
Clean hairline cell borders, flat badges, and institutional pagination.

- [ ] **Step 2: Update Chart.js styling in `templates/admin/dashboard.html`**
Ensure chart grid lines, tooltips, and background doughnut borders adapt cleanly to both light and dark themes using CSS variables.

- [ ] **Step 3: Run tests**
Run: `.venv/bin/python -m unittest discover tests/`
Expected: All tests pass.

- [ ] **Step 4: Commit**
```bash
git add static/css/style.css templates/admin/dashboard.html
git commit -m "modernize reports and admin analytics with monochrome styling"
```

---

### Task 7: Comprehensive Verification & Visual Audit

**Files:**
- Visual Verification: Screenshots via Headless Chrome (`/tmp/audit_light.png`, `/tmp/audit_dark.png`)
- Test: Full test suite

- [ ] **Step 1: Run complete test suite**
Run: `.venv/bin/python -m unittest discover tests/`
Expected: All tests pass.

- [ ] **Step 2: Capture screenshots of light and dark mode in Headless Chrome**
Capture screenshots of homepage and scanner pages in both modes to verify contrast, circular gauge, and typography.

- [ ] **Step 3: Review audit results and finalize**
Verify no layout clipping, no squashed elements, and full editorial aesthetics.
