# shadcn/ui Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform the TrustLens UI to 100% fidelity with the official shadcn/ui (Zinc theme) design system while maintaining native Flask Jinja2 server rendering and passing all unit and scanner test suites.

**Architecture:** Implement shadcn's official CSS design tokens and component classes in `static/css/style.css`, upgrade the global chrome and Lucide icons in `templates/base.html` and `templates/components/icons.html`, and refactor homepage and scanner interfaces into composable shadcn Card, Button, Badge, and Input structures.

**Tech Stack:** Flask, Jinja2, HTML5, Vanilla JavaScript, CSS custom properties (shadcn Zinc design tokens), Lucide SVG icons.

**Spec:** `docs/superpowers/specs/2026-10-03-shadcn-ui-redesign-design.md`

## Global Constraints

- **Theme Palette:** Pure Zinc theme (`--background: #ffffff`, `--foreground: #09090b` in light; `--background: #09090b`, `--foreground: #fafafa` in dark).
- **Radius:** Standard `0.5rem` (8px).
- **Single Accent:** Strict monochrome dominance (`--primary: #18181b` in light, `--primary: #fafafa` in dark). Colored signals (`--signal-safe`, `--signal-warning`, `--signal-danger`) strictly reserved for verification verdicts.
- **Invariants:** NEVER rename or remove form input IDs (`scanForm`, `url`, `email_text`, `job_text`, `chat_image`, `qr_image`, `payment_image`, `ingredient_input`, `claim_text`, `resultBox`, `themeToggle`).
- **Git Commits:** Simple English commit messages at all times.
- **Verification:** All 20 tests in `tests/` and the product validation suite must pass 100% after every task.

## Review Focus

1. **Light/Dark Contrast:** Input borders and background surfaces must maintain minimum 4.5:1 text contrast in both light and dark modes.
2. **Double Ring Focus:** Input focus rings must render cleanly with `box-shadow: 0 0 0 2px var(--background), 0 0 0 4px var(--ring)` without clipping in flex parents.
3. **Gauge Aspect Ratio:** Circular gauge meters must never distort into ellipses (`aspect-ratio: 1 / 1; flex-shrink: 0`).
4. **File Dropzone Drag Feedback:** Dropzones must clearly react on dragover/dragleave with border and surface transitions.
5. **Mobile Navigation Parity:** Mobile dropdowns and toggler buttons must function smoothly without broken responsive utility classes.

---

### Task 1: shadcn Zinc Design Tokens & Component Utility Classes

**Files:**
- Modify: `static/css/style.css`
- Test: `tests/`

**Interfaces:**
- Consumes: Existing CSS stylesheet
- Produces: Official shadcn Zinc tokens (`--background`, `--foreground`, `--card`, `--primary`, `--secondary`, `--muted`, `--accent`, `--destructive`, `--border`, `--input`, `--ring`, `--radius: 0.5rem`) and component classes (`.card`, `.btn`, `.badge`, `.input`, `.tabs-list`, `.dropdown-menu`, `.alert`)

- [ ] **Step 1: Check baseline test suite**
Run: `.venv/bin/python -m unittest discover tests/`
Expected: PASS (20 tests passed)

- [ ] **Step 2: Add shadcn Zinc design tokens to `static/css/style.css`**
Update `:root` and `[data-theme='dark']` blocks with the exact Zinc color definitions from the spec, mapping legacy token names (`--bg-canvas`, `--bg-surface`, `--text-primary`, `--border-subtle`, `--accent`) to their shadcn equivalents.

- [ ] **Step 3: Define shadcn component primitives in `static/css/style.css`**
Add styles for:
- Buttons: `.btn`, `.btn-default` / `.btn-primary` / `.btn-trust`, `.btn-secondary`, `.btn-outline`, `.btn-ghost`, `.btn-destructive`, `.btn-sm`, `.btn-lg`, `.btn-icon`
- Cards: `.card`, `.card-header`, `.card-title`, `.card-description`, `.card-content`, `.card-footer`
- Badges: `.badge`, `.badge-default`, `.badge-secondary`, `.badge-outline`, `.badge-destructive`, `.badge-safe`, `.badge-warning`
- Inputs: `.form-control-trust`, `.input`, `.textarea` with focus double ring
- Tabs: `.tabs-list`, `.tabs-trigger`
- Dropdowns: `.dropdown-menu`, `.dropdown-item`
- Alerts: `.alert`, `.alert-destructive`

- [ ] **Step 4: Run unit tests to confirm zero styling regressions**
Run: `.venv/bin/python -m unittest discover tests/`
Expected: PASS

- [ ] **Step 5: Commit changes**
Run:
```bash
git add static/css/style.css
git commit -m "add shadcn zinc tokens and component utility classes"
```

---

### Task 2: Global Chrome & Navigation Shell (Header, Theme Toggle, Footer, Lucide Icons)

**Files:**
- Modify: `templates/base.html`
- Modify: `templates/components/icons.html`
- Modify: `static/css/style.css`
- Test: `tests/`

**Interfaces:**
- Consumes: Task 1 tokens and button/dropdown classes
- Produces: shadcn-styled pinned navbar, theme switch button, 8-scanner dropdown, Lucide icons, and minimal footer

- [ ] **Step 1: Expand Lucide SVG icons in `templates/components/icons.html`**
Ensure clean 1.5px/1.75px Lucide vector paths for `shield`, `globe`, `mail`, `briefcase`, `message`, `qr`, `receipt`, `flask`, `scale`, `sun`, `moon`, `chevron-down`, `arrow-right`, `check`, `alert-circle`, `external-link`.

- [ ] **Step 2: Refine `templates/base.html` Navbar**
Style `.navbar-trust` with `background: var(--background); border-bottom: 1px solid var(--border);`.
Update brand mark to clean Lucide icon in a rounded-md neutral box (`border: 1px solid var(--border); background: var(--secondary)`).
Update theme toggle button to `.btn .btn-ghost .btn-icon`.
Update the 8-scanner dropdown menu with shadcn `.dropdown-menu` and `.dropdown-item` styling.

- [ ] **Step 3: Refine `templates/base.html` Footer**
Format footer with subtle top border (`1px solid var(--border)`), muted secondary typography, and Lucide brand mark.

- [ ] **Step 4: Run unit tests**
Run: `.venv/bin/python -m unittest discover tests/`
Expected: PASS

- [ ] **Step 5: Commit changes**
Run:
```bash
git add templates/base.html templates/components/icons.html static/css/style.css
git commit -m "modernize navigation header and footer with shadcn styling"
```

---

### Task 3: Modernize Homepage (Hero, Metrics, Scanner Cards)

**Files:**
- Modify: `templates/index.html`
- Modify: `static/css/style.css`
- Test: `tests/`

**Interfaces:**
- Consumes: Task 1 card & button components, Task 2 icons
- Produces: shadcn-aligned homepage with hero, metrics, and 8-scanner card grid

- [ ] **Step 1: Refactor Hero section in `templates/index.html`**
Update hero eyebrow badge to shadcn `.badge .badge-outline`.
Set typography tracking to tight `-0.03em`.
Use solid primary CTA (`.btn .btn-primary`) and outline CTA (`.btn .btn-outline`).
Format tabular metrics with clean borders and muted micro-labels.

- [ ] **Step 2: Refactor 8-Scanner Grid in `templates/index.html`**
Wrap each scanner in a shadcn `.card` container:
- `.card-header` with Lucide icon in `.bg-secondary` box, `.card-title`, and `.card-description`.
- `.card-footer` with clean arrow link indicator.

- [ ] **Step 3: Refactor "Why TrustLens" Feature Grid & Final CTA**
Align features and CTA block to flat surface cards with hairline borders.

- [ ] **Step 4: Run unit tests**
Run: `.venv/bin/python -m unittest discover tests/`
Expected: PASS

- [ ] **Step 5: Commit changes**
Run:
```bash
git add templates/index.html static/css/style.css
git commit -m "redesign homepage with shadcn cards and typography"
```

---

### Task 4: Scanner Form Interfaces & Drop Zones

**Files:**
- Modify: `templates/scanners/website_scanner.html`
- Modify: `templates/scanners/email_scanner.html`
- Modify: `templates/scanners/job_checker.html`
- Modify: `templates/scanners/whatsapp_scanner.html`
- Modify: `templates/scanners/qr_scanner.html`
- Modify: `templates/scanners/payment_analyzer.html`
- Modify: `templates/product_scanner.html`
- Modify: `templates/claim_scanner.html`
- Modify: `static/css/style.css`
- Test: `tests/` and `tests/test_product_scanner.py`

**Interfaces:**
- Consumes: Task 1 card/input/badge/button classes
- Produces: Consistent shadcn form interfaces across all 8 scanners

- [ ] **Step 1: Standardize URL, Email, Job, and Claim scanner forms**
Wrap scanner inputs in shadcn `.card` (`.card-header`, `.card-content`).
Style text inputs and textareas with `.form-control-trust` / `.input`.
Use `.btn .btn-primary` for submit buttons.
CRITICAL: Preserve all element IDs (`scanForm`, `url`, `email_text`, `job_text`, `claim_text`, `resultBox`).

- [ ] **Step 2: Standardize Image & Dropzone scanner forms (WhatsApp, QR, Payment, Product)**
Format `.drop-zone` with dashed border (`1.5px dashed var(--border)`), secondary background, and Lucide icons.
CRITICAL: Preserve file input IDs (`chat_image`, `qr_image`, `payment_image`, `ingredient_image`, `ingredient_input`).

- [ ] **Step 3: Run full scanner validation suites**
Run: `.venv/bin/python -m unittest discover tests/`
Run: `.venv/bin/python tests/test_product_scanner.py`
Expected: ALL PASS

- [ ] **Step 4: Commit changes**
Run:
```bash
git add templates/scanners/ templates/product_scanner.html templates/claim_scanner.html static/css/style.css
git commit -m "standardize scanner form cards and dropzones to shadcn style"
```

---

### Task 5: Circular Gauge & Forensic Result Cards

**Files:**
- Modify: `static/css/style.css`
- Modify: `static/js/main.js`
- Test: `tests/`

**Interfaces:**
- Consumes: Task 1 tokens and Task 4 scanner pages
- Produces: High-contrast result cards, tabular ledgers, and circular gauges

- [ ] **Step 1: Refine circular gauge styling in `static/css/style.css`**
Enforce `aspect-ratio: 1 / 1; flex-shrink: 0;` on `.gauge-wrap` and `.gauge-ring`.
Set track color to `var(--border)` and active ring color to semantic variables (`--signal-safe`, `--signal-warning`, `--signal-danger`).
Display score with bold tabular numbers.

- [ ] **Step 2: Style check tables and result badges**
Format `.chk-table` with hairline borders (`1px solid var(--border)`), subtle header text (`var(--muted-foreground)`), and tabular point columns.
Format verdict pills using shadcn `.badge` variants.

- [ ] **Step 3: Verify dynamic gauge rendering in `static/js/main.js`**
Confirm `TrustLens.renderGauge` and `TrustLens.renderRiskGauge` calculate conic gradients cleanly using `var(--border)`.

- [ ] **Step 4: Run unit tests**
Run: `.venv/bin/python -m unittest discover tests/`
Run: `.venv/bin/python tests/test_product_scanner.py`
Expected: ALL PASS

- [ ] **Step 5: Commit changes**
Run:
```bash
git add static/css/style.css static/js/main.js
git commit -m "update circular gauge and result cards with shadcn tokens"
```

---

### Task 6: Secondary Pages, Reports, Admin Dashboard & Final Verification

**Files:**
- Modify: `templates/reports/list.html`
- Modify: `templates/reports/detail.html`
- Modify: `templates/reports/submit.html`
- Modify: `templates/contact.html`
- Modify: `templates/about.html`
- Modify: `templates/admin/dashboard.html`
- Modify: `templates/admin/analytics.html`
- Modify: `static/css/style.css`
- Test: `tests/`

**Interfaces:**
- Consumes: Tasks 1-5 component library
- Produces: Unified shadcn styling across secondary views and admin analytics

- [ ] **Step 1: Refactor Scam Reports and Contact views**
Style reports table, report cards, filter tabs, and submission forms with shadcn `.card`, `.badge`, and `.input` components.

- [ ] **Step 2: Refactor Admin Dashboard & Analytics**
Style dashboard stat cards with `.card` and `.card-header`.
Adapt Chart.js colors to dynamic shadcn CSS variables (`--border`, `--muted-foreground`).

- [ ] **Step 3: Run comprehensive verification**
Run: `.venv/bin/python -m unittest discover tests/`
Run: `.venv/bin/python tests/test_product_scanner.py`
Expected: 100% tests passing.

- [ ] **Step 4: Commit changes and push to origin**
Run:
```bash
git add templates/reports/ templates/contact.html templates/about.html templates/admin/ static/css/style.css
git commit -m "refactor secondary pages and admin dashboard to shadcn design"
git push origin main
```
