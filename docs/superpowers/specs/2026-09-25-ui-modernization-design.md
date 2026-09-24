# Specification: UI Modernization, Theming & Clean Design System

**Date**: 2026-09-25  
**Status**: Pending Review  
**Theme**: Minimal Slate & Clean Tech (Linear / Vercel inspired)  
**System Target**: TrustLens AI Verification Platform

---

## 1. Overview & Objectives

TrustLens is an AI-based information verification platform providing 8 specialized scanners (Website, Email, WhatsApp, QR, Payment, Job, Product, Claim). The current user interface features an animated canvas particle system, heavy neon aurora gradients, and raw HTML emoji entities.

This specification defines the complete modernization of the TrustLens UI to achieve:
1. **Minimal, Professional Aesthetic**: Clean, quiet authority with high contrast, refined typography, and 1px borders inspired by modern developer/security tools (Linear, Vercel, Cloudflare).
2. **Dual-Theme Architecture (Dark & Light Modes)**: Automatic system preference detection (`prefers-color-scheme`) with an instant navbar toggle (Sun/Moon switch) stored in `localStorage`, engineered with zero Flash of Unstyled Content (FOUC).
3. **Pure SVG Vector Iconography**: Replace all raw platform-dependent emojis with sharp, consistent SVG vector icons.
4. **Unified 8-Scanner Navigation & Discovery**: Update navigation and hero showcase to cleanly present all 8 verification engines without cluttered dropdowns or hidden links.
5. **Component Standardization**: Consolidate disparate inline template styles into a centralized design system in `static/css/style.css` (trust score gauges, status badges, check tables, and drop zones).

---

## 2. Design Tokens & Theme Architecture

### 2.1 CSS Custom Properties Matrix

Theme tokens will be defined on `:root` with semantic defaults, and swapped via `[data-theme="dark"]` and `[data-theme="light"]`.

| Token Name | Dark Mode (Default) | Light Mode | Purpose |
| :--- | :--- | :--- | :--- |
| `--bg-canvas` | `#090d16` (Deep Slate) | `#f8fafc` (Off-white) | Base page background |
| `--bg-surface` | `#111726` (Card Slate) | `#ffffff` (Pure White) | Card & panel background |
| `--bg-surface-elevated` | `#182032` | `#f1f5f9` | Dropdowns, modals, hover states |
| `--bg-input` | `rgba(255, 255, 255, 0.04)` | `#ffffff` | Form input backgrounds |
| `--border-color` | `rgba(255, 255, 255, 0.10)` | `rgba(0, 0, 0, 0.09)` | Standard container borders |
| `--border-subtle` | `rgba(255, 255, 255, 0.05)` | `rgba(0, 0, 0, 0.05)` | Inner dividers and secondary borders |
| `--text-primary` | `#f8fafc` (Near White) | `#0f172a` (Deep Slate) | Headings, main content |
| `--text-secondary` | `#94a3b8` (Slate 400) | `#475569` (Slate 600) | Descriptions, subtitles (WCAG AA > 5.5:1) |
| `--text-tertiary` | `#64748b` (Slate 500) | `#94a3b8` (Slate 400) | Meta text, timestamps, captions |
| `--accent-primary` | `#6366f1` (Indigo 500) | `#4f46e5` (Indigo 600) | Primary buttons, active tabs, links |
| `--accent-focus` | `rgba(99, 102, 241, 0.35)` | `rgba(79, 70, 229, 0.25)` | Keyboard focus rings |
| `--trust-safe` | `#10b981` (Emerald) | `#059669` (Dark Emerald) | Safe status, score 80–100, pass checks |
| `--trust-safe-bg` | `rgba(16, 185, 129, 0.12)` | `rgba(5, 150, 105, 0.10)` | Safe pills and highlight backgrounds |
| `--trust-warning` | `#f59e0b` (Amber) | `#d97706` (Deep Amber) | Warning status, score 40–79 |
| `--trust-warning-bg`| `rgba(245, 158, 11, 0.12)` | `rgba(217, 119, 6, 0.10)` | Warning pills and alert backgrounds |
| `--trust-danger` | `#ef4444` (Rose) | `#dc2626` (Crimson) | Dangerous status, score 0–39 |
| `--trust-danger-bg` | `rgba(239, 68, 68, 0.12)` | `rgba(220, 38, 38, 0.10)` | Danger pills and alert backgrounds |
| `--shadow-card` | `0 4px 20px -2px rgba(0, 0, 0, 0.5)` | `0 4px 20px -2px rgba(15, 23, 42, 0.06)` | Card depth |
| `--shadow-nav` | `0 1px 3px 0 rgba(0, 0, 0, 0.3)` | `0 1px 3px 0 rgba(15, 23, 42, 0.08)` | Scrolled header border |

### 2.2 FOUC Prevention & Persistence

To eliminate Flash of Unstyled Content when switching pages:
1. In `templates/base.html` inside `<head>`:
   ```html
   <meta name="color-scheme" content="light dark">
   <script>
     (function() {
       const saved = localStorage.getItem("trustlens-theme");
       if (saved === "light" || saved === "dark") {
         document.documentElement.setAttribute("data-theme", saved);
       } else if (window.matchMedia && window.matchMedia("(prefers-color-scheme: light)").matches) {
         document.documentElement.setAttribute("data-theme", "light");
       } else {
         document.documentElement.setAttribute("data-theme", "dark");
       }
     })();
   </script>
   ```
2. Interactive Theme Switcher button in navbar with SVG Sun and Moon icons. Toggling updates `data-theme` on `<html>` and writes to `localStorage`.
3. System preference listener (`matchMedia("(prefers-color-scheme: dark)").addEventListener("change", ...)`) dynamically responds if the user hasn't explicitly locked a preference.

---

## 3. Visual System & Background Architecture

### 3.1 Background Refactoring
- **Removal**: Delete `#particles-js` canvas and the 3 massive neon `.bg-aurora` radial gradients.
- **Replacement**: A refined, subtle technical grid pattern (`.bg-subtle-grid`) created with a CSS radial/linear dot-mesh:
  ```css
  .bg-subtle-grid {
    position: fixed;
    inset: 0;
    z-index: -1;
    background-color: var(--bg-canvas);
    background-image: radial-gradient(var(--border-subtle) 1px, transparent 1px);
    background-size: 24px 24px;
    mask-image: radial-gradient(ellipse at 50% 0%, black 70%, transparent 100%);
    -webkit-mask-image: radial-gradient(ellipse at 50% 0%, black 70%, transparent 100%);
    pointer-events: none;
  }
  ```
- Delivers clean modern texture without distracting animations or high GPU utilization.

### 3.2 Glassmorphism & Elevation
- Replace heavy blur glass panels with crisp 1px borders, subtle surface elevations (`--bg-surface`), and optional slight blur (`backdrop-filter: blur(8px)`).
- Ensure cards in both dark and light modes have clear contrast against the canvas.

---

## 4. Iconography & Brand System

### 4.1 Reusable Vector SVG System
All raw HTML character entities will be replaced with clean vector SVGs (viewBox 0 0 24 24, stroke-width 1.75px, fill none, stroke currentColor):
1. **Brand Mark**: A stylized shield containing an optical verification lens.
2. **Website Scanner**: Globe with verification checkmark.
3. **Email Scanner**: Mail envelope with shield badge.
4. **WhatsApp Scanner**: Message bubble with search/shield.
5. **QR Scanner**: QR viewfinder grid.
6. **Payment Analyzer**: Receipt / credit card forensic marker.
7. **Job Checker**: Briefcase with alert badge.
8. **Product Scanner**: Barcode / ingredient flask.
9. **Claim Checker**: Scale of truth / quote validation badge.
10. **Theme Toggle**: Dual Sun & Moon icon.

### 4.2 Brand Typography & Hierarchy
- Clean typography using system sans stack: `system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif`.
- Crisp heading weights with tight tracking (`letter-spacing: -0.025em`).

---

## 5. Navigation & Layout Structure

### 5.1 Simplified Top Navigation
Replace the split `.nav-hide-md` / `.nav-drop-lg` code with a clean, responsive layout:
- **Brand**: Shield-Lens SVG + `Trust`**Lens**
- **Nav Links**:
  - **Home**
  - **Scanners** (Dropdown featuring all 8 engines organized with icons and descriptions)
  - **Scam Reports** (Community intelligence feed)
  - **Awareness** (Educational guides)
  - **About**
  - **Contact**
- **Right Action Cluster**:
  - Theme Toggle Button (Light/Dark mode)
  - Authenticated: Dashboard link + User badge + Logout
  - Unauthenticated: Sign In + Get Started

### 5.2 Homepage Scanner Grid
Update the "Six scanners" section on `templates/index.html` to showcase all **8 verification engines** in a balanced 4x2 responsive grid with clean card hover states, badge indicators, and consistent SVG icons.

---

## 6. Scanner Component Standardization

### 6.1 Unified Scanner Form & Drop Zones
- Clean, focused form inputs with distinct focus rings (`box-shadow: 0 0 0 2px var(--accent-focus)`).
- Image drag-and-drop zones (`.drop-zone`):
  - Clean dashed border with smooth drag-over highlight.
  - SVG upload icon.
  - Clear file name and size preview chip upon selection with a quick "remove" button.

### 6.2 Standardized Results Component
Consolidate results markup across all scanners into shared CSS classes:
- **Gauge Ring**: Reusable conic-gradient gauge ring with crisp center score and status label.
- **Summary Pill**: Unified `.status-badge` (`.status-safe`, `.status-warning`, `.status-danger`).
- **Signal Breakdown Cards**: Unified positive, warning, and deduction check rows with clear point badges (`+10`, `-15`, `0`).

---

## 7. Implementation Boundaries & Verification Plan

### 7.1 Files to Modify
- `static/css/style.css`: Redesign tokens, dark/light modes, grid background, buttons, cards, drop zones, gauges, badges, check tables.
- `static/js/main.js`: Theme toggle logic with `localStorage`, remove particles canvas code, update loading and gauge animations.
- `templates/base.html`: Modernized header, SVG brand mark, theme toggle button, streamlined nav dropdown, remove `#particles-js`.
- `templates/index.html`: 8-scanner grid, SVG icons, updated stats.
- `templates/dashboard.html`: Stat cards and recent scans table styling in light/dark.
- `templates/scanners/`: (website, email, job, whatsapp, qr, payment, product, claim) - migrate inline styles to standard CSS classes and SVG icons.
- `templates/admin/`: Nav sidebar and dashboard styling parity in both themes.

### 7.2 Safety & Regression Constraints
- **Zero API or logic disruption**: All scanner form input IDs, endpoints (`/api/scan-*`), and JSON response bindings (`TrustLens.apiPost`) must remain strictly unchanged.
- **100% Test Suite Green**: The existing 20-test discovery suite and scanner regression suites must continue to pass with zero failures.

---

## 8. Review & Sign-Off

Upon approval of this specification, the implementation plan will be created via `writing-plans` skill.

