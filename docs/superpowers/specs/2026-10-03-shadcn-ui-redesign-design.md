# TrustLens shadcn/ui Design System Specification

**Date:** 2026-10-03  
**Status:** Approved  
**Reference:** [shadcn/ui Design System](https://ui.shadcn.com) (Zinc Theme)

---

## 1. Executive Summary & Objective

Transform the TrustLens web platform UI into the **shadcn/ui** design system (Zinc base palette), giving the application an austere, modern, high-precision technical interface reminiscent of Vercel, Linear, and modern developer infrastructure.

The implementation preserves the native Python Flask and Jinja2 server-rendered architecture (preventing heavy Node/React build overhead, routing complications, or Vercel serverless bundle limits) while providing 100% fidelity to shadcn/ui's design tokens, typography, component geometry, interactive focus rings, and Lucide iconography.

---

## 2. Design System Tokens (Zinc Palette)

All design tokens are defined as CSS custom properties on `:root` (Light mode) and `[data-theme='dark']` (Dark mode) in `static/css/style.css`:

```css
:root {
  /* shadcn/ui Light (Zinc) */
  --background: #ffffff;
  --foreground: #09090b;

  --card: #ffffff;
  --card-foreground: #09090b;

  --popover: #ffffff;
  --popover-foreground: #09090b;

  --primary: #18181b;
  --primary-foreground: #fafafa;

  --secondary: #f4f4f5;
  --secondary-foreground: #18181b;

  --muted: #f4f4f5;
  --muted-foreground: #71717a;

  --accent: #f4f4f5;
  --accent-foreground: #18181b;

  --destructive: #ef4444;
  --destructive-foreground: #fafafa;

  --border: #e4e4e7;
  --input: #e4e4e7;
  --ring: #18181b;

  --radius: 0.5rem; /* 8px standard shadcn radius */

  /* Semantic trust verification signals */
  --signal-safe: #10b981;
  --signal-safe-bg: #ecfdf5;
  --signal-safe-border: #a7f3d0;

  --signal-warning: #f59e0b;
  --signal-warning-bg: #fffbeb;
  --signal-warning-border: #fde68a;

  --signal-danger: #ef4444;
  --signal-danger-bg: #fef2f2;
  --signal-danger-border: #fecaca;

  /* Legacy compatibility aliases */
  --bg-canvas: var(--background);
  --bg-surface: var(--card);
  --bg-surface-elevated: var(--secondary);
  --text-primary: var(--foreground);
  --text-secondary: var(--muted-foreground);
  --text-muted: var(--muted-foreground);
  --border-subtle: var(--border);
  --border-strong: #d4d4d8;
  --accent-primary: var(--primary);
}

[data-theme='dark'] {
  /* shadcn/ui Dark (Zinc) */
  --background: #09090b;
  --foreground: #fafafa;

  --card: #09090b;
  --card-foreground: #fafafa;

  --popover: #09090b;
  --popover-foreground: #fafafa;

  --primary: #fafafa;
  --primary-foreground: #18181b;

  --secondary: #27272a;
  --secondary-foreground: #fafafa;

  --muted: #27272a;
  --muted-foreground: #a1a1aa;

  --accent: #27272a;
  --accent-foreground: #fafafa;

  --destructive: #7f1d1d;
  --destructive-foreground: #fafafa;

  --border: #27272a;
  --input: #27272a;
  --ring: #d4d4d8;

  /* Dark mode semantic trust signals */
  --signal-safe: #34d399;
  --signal-safe-bg: rgba(16, 185, 129, 0.12);
  --signal-safe-border: rgba(16, 185, 129, 0.25);

  --signal-warning: #fbbf24;
  --signal-warning-bg: rgba(245, 158, 11, 0.12);
  --signal-warning-border: rgba(245, 158, 11, 0.25);

  --signal-danger: #f87171;
  --signal-danger-bg: rgba(239, 68, 68, 0.12);
  --signal-danger-border: rgba(239, 68, 68, 0.25);

  /* Legacy compatibility aliases */
  --bg-canvas: var(--background);
  --bg-surface: #121215;
  --bg-surface-elevated: var(--secondary);
  --text-primary: var(--foreground);
  --text-secondary: var(--muted-foreground);
  --text-muted: #71717a;
  --border-subtle: var(--border);
  --border-strong: #3f3f46;
  --accent-primary: var(--primary);
}
```

---

## 3. Component Architecture & Specifications

### 3.1 Button (`.btn` / `.ui-btn`)
Follows the button variant system from shadcn:
- **Default (`.btn-default` / `.btn-primary` / `.btn-trust`)**:
  - `background: var(--primary); color: var(--primary-foreground); border-radius: var(--radius);`
  - Font: 14px (0.875rem), weight 500.
  - Hover: Opacity 0.9 or slight brightness shift.
- **Secondary (`.btn-secondary`)**:
  - `background: var(--secondary); color: var(--secondary-foreground);`
- **Outline (`.btn-outline` / `.btn-ghost-outline`)**:
  - `border: 1px solid var(--input); background: transparent; color: var(--foreground);`
  - Hover: `background: var(--accent); color: var(--accent-foreground);`
- **Ghost (`.btn-ghost`)**:
  - `background: transparent; color: var(--foreground);`
  - Hover: `background: var(--accent); color: var(--accent-foreground);`
- **Destructive (`.btn-destructive`)**:
  - `background: var(--destructive); color: var(--destructive-foreground);`
- **Sizes**:
  - `btn-sm`: height 36px, padding `0 12px`, font-size 13px.
  - `btn-md`: height 40px, padding `0 16px`, font-size 14px.
  - `btn-lg`: height 44px, padding `0 24px`, font-size 15px.
  - `btn-icon`: square 36x36px or 40x40px, display flex, align/justify center.

### 3.2 Card System (`.card`)
Structural breakdown matching shadcn Card:
- Container: `border: 1px solid var(--border); background: var(--card); border-radius: var(--radius); box-shadow: 0 1px 2px 0 rgba(0,0,0,0.05);`
- `.card-header`: `padding: 1.5rem 1.5rem 0.5rem 1.5rem; display: flex; flex-direction: column; gap: 0.375rem;`
- `.card-title`: `font-size: 1.25rem; font-weight: 600; line-height: 1.2; letter-spacing: -0.02em; color: var(--card-foreground);`
- `.card-description`: `font-size: 0.875rem; color: var(--muted-foreground); line-height: 1.4;`
- `.card-content`: `padding: 1.5rem;`
- `.card-footer`: `padding: 0 1.5rem 1.5rem 1.5rem; display: flex; align-items: center;`

### 3.3 Form Inputs (`.form-control-trust`, `.input`, `.textarea`)
- `height: 40px; border-radius: var(--radius); border: 1px solid var(--input); background: transparent; padding: 0.5rem 0.75rem; color: var(--foreground); font-size: 0.875rem;`
- Focus: `outline: none; box-shadow: 0 0 0 2px var(--background), 0 0 0 4px var(--ring); border-color: var(--ring);`
- Drop Zone (`.drop-zone`): `border: 1.5px dashed var(--border); border-radius: var(--radius); background: var(--secondary); transition: all 0.15s ease;`
- Dragover: `border-color: var(--ring); background: var(--card);`

### 3.4 Badge (`.badge`)
- Micro-pill indicator: `inline-flex; align-items: center; border-radius: 9999px; border: 1px solid transparent; padding: 0.2rem 0.65rem; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em;`
- Variants:
  - Default: `background: var(--primary); color: var(--primary-foreground);`
  - Secondary: `background: var(--secondary); color: var(--secondary-foreground);`
  - Outline: `border-color: var(--border); color: var(--foreground);`
  - Destructive: `background: var(--destructive); color: var(--destructive-foreground);`
  - Safe: `background: var(--signal-safe-bg); color: var(--signal-safe); border-color: var(--signal-safe-border);`
  - Warning: `background: var(--signal-warning-bg); color: var(--signal-warning); border-color: var(--signal-warning-border);`

### 3.5 Tabs (`.tabs-list`, `.tabs-trigger`)
- `.tabs-list`: `display: inline-flex; height: 40px; align-items: center; background: var(--muted); border-radius: var(--radius); padding: 4px;`
- `.tabs-trigger`: `padding: 6px 12px; font-size: 0.875rem; font-weight: 500; border-radius: calc(var(--radius) - 2px); color: var(--muted-foreground); cursor: pointer; transition: all 0.15s ease;`
- `.tabs-trigger.active`: `background: var(--card); color: var(--card-foreground); box-shadow: 0 1px 3px rgba(0,0,0,0.1);`

### 3.6 Alerts (`.alert`)
- Container: `border: 1px solid var(--border); border-radius: var(--radius); padding: 1rem; position: relative;`
- Destructive Alert: `border-color: var(--signal-danger-border); background: var(--signal-danger-bg); color: var(--signal-danger);`

### 3.7 Lucide Icons (`templates/components/icons.html`)
- All vector SVG icons will adopt 1.5px/1.75px stroke widths, square optical boxes, and standard Lucide shapes.

---

## 4. Architectural Invariants & Non-Functional Requirements

1. **No Breaking ID Changes**:
   - `scanForm`, `url`, `email_text`, `job_text`, `chat_image`, `qr_image`, `payment_image`, `ingredient_input`, `ingredient_image`, `claim_text`, `resultBox`, `themeToggle`.
2. **Backend Route Integrity**:
   - All 8 scanner endpoints (`/scanners/*`, `/product-scanner`, `/claim-checker`) and reporting routes remain intact.
3. **No Heavy JavaScript Bundlers**:
   - Everything remains pure CSS and HTML/Jinja2 templates, preserving fast page loads and small deployment bundle size on Vercel.
4. **Automated Test Suite**:
   - 100% of unit tests (`python -m unittest discover tests/`) and validation suites must pass after each refactoring stage.

---

## 5. Implementation Roadmap

1. **Phase 1: Design Tokens & Base CSS**: Introduce Zinc color tokens, font hierarchy, and component classes in `static/css/style.css`.
2. **Phase 2: Global Chrome & Navigation**: Modernize `templates/base.html` header, theme toggle, and footer to shadcn style.
3. **Phase 3: Homepage Modernization**: Update `templates/index.html` hero, metrics, and scanner cards to shadcn card and badge structures.
4. **Phase 4: Scanner Interfaces & Results**: Standardize all scanner templates (`templates/scanners/*.html`, `templates/product_scanner.html`, `templates/claim_scanner.html`) with shadcn cards, form inputs, dropzones, and alert banners.
5. **Phase 5: Secondary Pages & Verification**: Polish reports, admin views, and run full test suites.
