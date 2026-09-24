# UI Modernization & Dual-Theming Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform the TrustLens UI into a minimal, clean, professional modern interface with dynamic dual-theme (Dark & Light) support, vector SVG icons, unified 8-scanner discovery, and standardized component styles.

**Architecture:** CSS custom property tokens defined on `:root`, `[data-theme="dark"]`, and `[data-theme="light"]` with `color-scheme: light dark`. A persistent theme toggle in the navigation bar using an inline head script to prevent FOUC. Centralization of all ad-hoc scanner styles into `static/css/style.css`.

**Tech Stack:** Bootstrap 5.3, CSS Custom Properties, Vanilla JavaScript (ES6+), Jinja2 templates, SVG vector icons.

**Spec:** `docs/superpowers/specs/2026-09-25-ui-modernization-design.md`

## Global Constraints

- Never break or rename existing form input IDs, classes required by scripts, API endpoints (`/api/scan-*`), or JSON payload contracts.
- Strictly adhere to WCAG AA contrast standards (minimum 4.5:1 for normal text, 3:1 for large text and UI components).
- Zero Flash of Unstyled Content (FOUC) when loading pages in user-pinned light or dark themes.
- No raw HTML character entity emojis (`&#128...`) for platform iconography; use inline vector SVGs with consistent stroke weights.
- All 20 existing unit/security tests and scanner validation suites must continue passing 100%.

## Review Focus

1. **Light Mode Legibility**: Contrast on white card surfaces against borders and text must remain crisp and readable without washed-out grays.
2. **FOUC on Navigation**: Ensure the theme is read from `localStorage` synchronously in `<head>` before body render.
3. **Responsive Mobile Navigation**: Clean collapse/expand on small screens without overlapping buttons or broken dropdowns.
4. **Scanner Form ID Integrity**: Scanning scripts (`main.js` and scanner-specific handlers) must continue to locate their expected DOM elements without errors.
5. **Score Gauge Consistency**: Conic gradient trust score gauge must render cleanly in both dark and light modes with legible center typography.

---

### Task 1: Design Tokens, Dual-Theming Architecture & Anti-FOUC Setup

**Files:**
- Modify: `static/css/style.css`
- Modify: `static/js/main.js`
- Modify: `templates/base.html`

- [x] **Step 1: Define CSS Theme Variables in `static/css/style.css`**
  - Define semantic tokens on `:root`, `[data-theme="dark"]`, and `[data-theme="light"]`:
    - Canvas: `--bg-canvas` (`#090d16` vs `#f8fafc`)
    - Surface: `--bg-surface` (`#111726` vs `#ffffff`), `--bg-surface-elevated` (`#182032` vs `#f1f5f9`)
    - Borders: `--border-color` (`rgba(255,255,255,0.10)` vs `rgba(0,0,0,0.09)`), `--border-subtle`
    - Typography: `--text-primary`, `--text-secondary`, `--text-tertiary`
    - Semantic Accents: `--trust-safe` (`#10b981`), `--trust-warning` (`#f59e0b`), `--trust-danger` (`#ef4444`), `--accent-primary` (`#6366f1`)
  - Set `color-scheme: light dark;` on `:root`.
  - Replace `.bg-aurora` and remove `#particles-js` styling; add `.bg-subtle-grid` dot-mesh background.

- [x] **Step 2: Add Anti-FOUC Script & Theme Toggle Button to `templates/base.html`**
  - Add inline theme detector script in `<head>`.
  - Remove `#particles-js` canvas and replace `<div class="bg-aurora"></div>` with `<div class="bg-subtle-grid"></div>`.
  - Add the theme toggle button in the navbar right action cluster with inline Sun/Moon SVGs.

- [x] **Step 3: Implement Theme Switcher Logic in `static/js/main.js`**
  - Add `TrustLens.toggleTheme()` and event listener for the theme toggle button.
  - Sync with `localStorage.setItem("trustlens-theme", theme)`.
  - Remove obsolete particles animation loop code from `main.js`.

- [x] **Step 4: Verify Theme Switching**
  - Test toggling dark/light modes and verify `data-theme` attribute updates on `<html>` and persists across reloads.

- [x] **Step 5: Commit**
  - Commit as: `add dual theme tokens and navbar theme toggle`

---

### Task 2: Vector SVG Iconography System & Brand Mark

**Files:**
- Create: `templates/components/icons.html`
- Modify: `templates/base.html`
- Modify: `static/css/style.css`

- [ ] **Step 1: Create Reusable SVG Icon Macro in `templates/components/icons.html`**
  - Build Jinja macros for standard vector icons (shield, lens, globe, mail, message, qr, receipt, briefcase, flask, scale, sun, moon, check, x-mark, alert).
  - Use 24x24 viewBox, `fill="none"`, `stroke="currentColor"`, `stroke-width="1.75"`.

- [ ] **Step 2: Update Brand Mark and Navigation Icons in `templates/base.html`**
  - Replace `&#128274;` brand mark with a modern shield-lens vector SVG.
  - Style `.brand-mark` with clean indigo-emerald accent gradient or crisp monochrome.

- [ ] **Step 3: Commit**
  - Commit as: `create vector svg icons and update brand mark`

---

### Task 3: Modern Navigation & 8-Scanner Dropdown Architecture

**Files:**
- Modify: `templates/base.html`
- Modify: `static/css/style.css`

- [ ] **Step 1: Streamline Header Navigation in `templates/base.html`**
  - Eliminate confusing duplicate classes (`.nav-hide-md`, `.nav-drop-lg`, `#moreMenuT`, `#moreMenuD`).
  - Create a unified "Scanners" dropdown containing all 8 engines:
    1. Website Scanner (Phishing & Domain Checks)
    2. Email Scanner (Phishing & Urgency Analysis)
    3. Job Checker (Offer Letter & Recruiter Fraud)
    4. WhatsApp Scanner (Chat Screenshot OCR)
    5. QR Scanner (Destination & Payload Safety)
    6. Payment Analyzer (Fake Screenshot & UPI Validation)
    7. Product Scanner (Ingredient Safety & Database Lookup)
    8. Claim Checker (Truth & Fact Verification)
  - Ensure standard direct nav links for Home, Scam Reports, Awareness, About, Contact.

- [ ] **Step 2: Update Navbar Styling for Light and Dark Modes in `static/css/style.css`**
  - Style `.navbar-trust` with `--bg-surface` translucent backdrop, subtle bottom border, and crisp text links.
  - Style dropdown menu (`.nav-dropdown-menu`) with clean elevation and active indicator states.

- [ ] **Step 3: Verify Responsive Navbar**
  - Verify dropdown expands cleanly on desktop and mobile viewports.

- [ ] **Step 4: Commit**
  - Commit as: `unify navigation and add 8 scanner dropdown`

---

### Task 4: Homepage (Landing Page) Modernization

**Files:**
- Modify: `templates/index.html`
- Modify: `static/css/style.css`

- [ ] **Step 1: Modernize Hero & Stats in `templates/index.html`**
  - Replace hero badge emoji with SVG shield.
  - Update stats to highlight "8 AI Scanners", "100% Transparent Scoring", and "Free to Verify".
  - Clean up preview card on the hero right side with SVG icons instead of colored bullets.

- [ ] **Step 2: Expand Scanner Grid to All 8 Tools in `templates/index.html`**
  - Update tools array to include Product Scanner and Claim Checker alongside the other 6 tools.
  - Replace tool icon emojis with corresponding vector SVG icons.
  - Refine `.tool-icon` and card hover styling in `style.css`.

- [ ] **Step 3: Modernize "Why TrustLens" & CTA Sections**
  - Replace checkmark emojis with crisp SVG checks.
  - Update cards and buttons with consistent theme variables.

- [ ] **Step 4: Commit**
  - Commit as: `modernize homepage and showcase all 8 scanners`

---

### Task 5: Standardize Scanner Form Controls, Drop Zones & Result Gauges

**Files:**
- Modify: `static/css/style.css`
- Modify: `static/js/main.js`
- Modify: `templates/scanners/website_scanner.html`
- Modify: `templates/scanners/email_scanner.html`
- Modify: `templates/scanners/job_checker.html`
- Modify: `templates/scanners/whatsapp_scanner.html`
- Modify: `templates/scanners/qr_scanner.html`
- Modify: `templates/scanners/payment_analyzer.html`
- Modify: `templates/product_scanner.html`
- Modify: `templates/claim_scanner.html`

- [ ] **Step 1: Consolidate Shared Scanner Component Styles in `static/css/style.css`**
  - Standardize `.chk-table`, `.chk-ico`, `.chk-name`, `.chk-pts`, `.chk-detail`.
  - Standardize `.gauge-ring`, `.gauge-inner`, and score typography.
  - Standardize `.drop-zone`, `.dz-icon`, `.dz-text`, dragover active state, and file preview badge.
  - Standardize status badges (`.status-pill.badge-safe`, `badge-warning`, `badge-dangerous`).

- [ ] **Step 2: Clean up Scanner Templates**
  - Remove duplicate inline `<style>` tags from scanner templates.
  - Replace emoji headers (e.g. `&#128270; WEBSITE SCANNER`) with clean SVG badges.
  - Ensure all form IDs (`scanForm`, `url`, `email_text`, `ingredient_input`, etc.) remain 100% intact.

- [ ] **Step 3: Update `static/js/main.js` Drop Zone and File Upload UX**
  - Add dragenter/dragover/dragleave/drop handlers to `.drop-zone` with active visual state.
  - Display selected file name and size with a clear "x" remove button.

- [ ] **Step 4: Commit**
  - Commit as: `standardize scanner forms drop zones and result cards`

---

### Task 6: Dashboard, Scam Reports & Admin Panel Polish

**Files:**
- Modify: `templates/dashboard.html`
- Modify: `templates/scam_reports.html`
- Modify: `templates/admin/_nav.html`
- Modify: `templates/admin/dashboard.html`
- Modify: `templates/components/report_status.html`
- Modify: `static/css/style.css`

- [ ] **Step 1: Update Dashboard and Report Cards**
  - Ensure stats cards (`.stat-card`), table rows, and update notifications adapt seamlessly to light and dark themes.
  - Replace emojis on dashboard empty states with SVG icons.

- [ ] **Step 2: Update Admin Navigation & Tables**
  - Replace emojis in `templates/admin/_nav.html` with vector SVGs.
  - Ensure admin sidebar and table borders have clear contrast in light and dark modes.

- [ ] **Step 3: Commit**
  - Commit as: `polish dashboard scam reports and admin panels`

---

### Task 7: Comprehensive Regression Verification & Test Suite Gate

**Files:**
- Execute: Test discovery suite
- Execute: Scanner validation scripts

- [ ] **Step 1: Run Full Unittest Discovery Suite**
  - Run: `.venv/bin/python -m unittest discover tests/`
  - Ensure 20/20 tests pass.

- [ ] **Step 2: Run Scanner Validation Suites**
  - Run: `.venv/bin/python tests/test_email_scanner.py`
  - Run: `.venv/bin/python tests/test_claim_scanner.py`
  - Run: `.venv/bin/python tests/test_product_scanner.py`
  - Ensure 100% pass across all scanner benchmarks.

- [ ] **Step 3: Verify Visual & Theme Integrity**
  - Check dark and light mode rendering across pages.
  - Verify zero console errors and clean layout.

- [ ] **Step 4: Commit & Close Out**
  - Commit any final polish and confirm completion.

