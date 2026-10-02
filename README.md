# TrustLens – AI Based Information Verification System

TrustLens is a production-grade multi-vector information verification web application designed to detect scams, fraud, counterfeit products, and misinformation. Users can analyze websites, emails, job offers, WhatsApp chat screenshots, QR codes, payment receipts, product ingredient labels, and factual claims. Every scan produces an explainable **0–100 trust score** backed by transparent heuristic checks.

---

## Quick Navigation

- [How to Run Step by Step](#how-to-run-step-by-step)
- [macOS Port Conflict Notice (Important)](#macos-port-conflict-notice-important)
- [All 8 Verification Engines](#all-8-verification-engines)
- [Default Admin Credentials](#default-admin-credentials)
- [Platform Features](#platform-features)
- [Project Documentation](#project-documentation)
- [Project Structure](#project-structure)

---

## How to Run Step by Step

Follow these steps to set up and run TrustLens locally on your system:

### Step 1: Clone or Open the Repository

Open your terminal or command prompt and navigate to the project directory:

```bash
cd /path/to/trustlens-fresh
```

### Step 2: Create a Virtual Environment

It is recommended to use an isolated Python virtual environment:

**On macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**On Windows:**
```cmd
python -m venv .venv
.venv\Scripts\activate
```

### Step 3: Install Required Dependencies

Ensure you have Python 3.10+ installed, then install all project requirements:

```bash
pip install -r requirements.txt
```

> **Note on OCR Models:** On first use of image-based scanners (WhatsApp, Payment, Product), `EasyOCR` will automatically download lightweight OCR model weights (~80MB).

### Step 4: Configure Environment Variables

Create your local `.env` configuration from the provided template:

```bash
cp .env.example .env
```

The application runs immediately with zero-config **SQLite** defaults. You can adjust settings in `.env` if desired:
- `SECRET_KEY`: Random secret key for session security.
- `USE_MYSQL`: Set to `0` for SQLite (default) or `1` for MySQL.
- `ADMIN_EMAIL`: Default administrator email (`gunjbazaz143@gmail.com`).
- `ADMIN_PASSWORD`: Default administrator password (`Admin@12345`).
- `MAIL_USERNAME` / `MAIL_PASSWORD`: Optional SMTP credentials for email alerts.

### Step 5: Start the Development Server

#### On macOS (Recommended: Port 5001)

```bash
PORT=5001 python run.py
```

#### On Windows / Linux (Port 5000)

```bash
python run.py
```

Alternatively, you can launch via:
```bash
PORT=5001 python app.py
```

### Step 6: Access the Application

Open your browser and navigate to:
- **Local Application URL:** [http://127.0.0.1:5001](http://127.0.0.1:5001) (or [http://127.0.0.1:5000](http://127.0.0.1:5000))
- **Admin Portal:** [http://127.0.0.1:5001/admin](http://127.0.0.1:5001/admin)

The database, schema tables, and product knowledge base (142 ingredients and 27 product records) are created automatically on first boot.

---

## macOS Port Conflict Notice (Important)

> [!WARNING]
> On macOS (Monterey, Ventura, Sonoma, Sequoia), the system **AirPlay Receiver** service listens on port `5000` by default (`ControlCenter`). Attempting to run Flask on port `5000` will return `403 Forbidden` or `Port 5000 not allowed for HTTP`.
> 
> **Always use `PORT=5001 python run.py` when running on macOS.**

---

## Default Admin Credentials

On initial boot, TrustLens provisions the bootstrap administrator:

- **Email:** `gunjbazaz143@gmail.com` (fallback: `admin@trustlens.io`)
- **Password:** `Admin@12345`
- **Admin Route:** `/admin`

---

## All 8 Verification Engines

TrustLens features eight specialized verification engines accessible via the unified navigation menu:

| # | Engine | Route | Core Verification Checks |
| :-: | :--- | :--- | :--- |
| **1** | **Website Scanner** | `/website-scanner` | 31 checks: SSL/TLS, domain age, suspicious TLDs, raw-IP hosts, phishing keywords, and admin blacklist. |
| **2** | **Email Scanner** | `/email-scanner` | Sender domain mismatch, phishing urgency patterns, malicious links, free-mail address cues. |
| **3** | **Job Checker** | `/job-checker` | Advance fee detection, interview via unofficial chat apps, unrealistic compensation, vague company domains. |
| **4** | **WhatsApp Scanner** | `/whatsapp-scanner` | EasyOCR analysis of chat screenshots categorized into lottery, OTP/KYC, customs courier, and crypto scams. |
| **5** | **QR Scanner** | `/qr-scanner` | Multi-engine decoding (`zxing-cpp`, `pyzbar`, `opencv`), URL threat extraction, payment command analysis. |
| **6** | **Payment Analyzer** | `/payment-analyzer` | Forensics on UPI screenshots (GPay, PhonePe, Paytm), UTR transaction format verification, and font tampering detection. |
| **7** | **Product Scanner** | `/product-scanner` | Label ingredient OCR extraction matched against reference toxicological database (142+ chemicals, 27+ product profiles). |
| **8** | **Claim Checker** | `/claim-checker` | Fact-checking engine verifying claims and viral rumors against authoritative reference patterns. |

---

## Platform Features

- **Institutional Editorial UI**: Clean, high-trust design system inspired by Linear, Stripe Press, and Vercel.
- **Native Dual-Theming**: Instant anti-FOUC theme switching between Light (`#fbfbfb`/`#ffffff`) and Dark (`#09090b`/`#121215`) modes with `?theme=light` / `?theme=dark` support.
- **Explainable Circular Score Gauges**: Strict 1:1 circular meters displaying 0–100 scores with tabular typography and clear check attribution.
- **Community Scam Reports Portal**: Public portal (`/scam-reports`) with user submission and administrative verification workflow.
- **Dynamic Threat Blacklist**: Real-time domain and entity blocking with immediate warning banners.
- **Admin Analytics Dashboard**: Dynamic Chart.js charts for scan volume, risk distribution, fraud type ranking, and user growth with real-time theme adaptation.
- **Automated Email Alerts**: Background notifications for scam reports and contact form inquiries.

---

## Project Documentation

For deeper architectural and implementation details, consult the `docs/` directory:

- [Project Guide & In-Depth Specifications](file:///Users/dineshchoudhary/Developer/kavita/trustlens-fresh/docs/GETTING_STARTED_AND_SPECIFICATIONS.md): Complete feature specifications, API contracts, database schema, and test guides.
- [Architecture & System Overview](file:///Users/dineshchoudhary/Developer/kavita/trustlens-fresh/docs/ARCHITECTURE.md): Technical stack, MVC patterns, service pipelines, and model definitions.
- [Design Specifications](file:///Users/dineshchoudhary/Developer/kavita/trustlens-fresh/docs/superpowers/specs/2026-09-27-institutional-editorial-redesign-design.md): Design tokens, typography hierarchy, and surface principles.

---

## Running Automated Tests

To run the automated unit test suite:

```bash
# Ensure virtual environment is active
source .venv/bin/activate

# Run all unit tests
python -m unittest discover tests/
```

All 20 unit tests should pass with `OK`.

---

## Project Structure

```
.
├── app.py                 # WSGI entry point
├── app_factory.py         # Flask application factory (blueprints, extensions, errors)
├── run.py                 # Development runner (respects PORT environment variable)
├── config.py              # Centralized environment configuration
├── requirements.txt       # Dependencies
├── .env.example           # Environment template
├── database/              # DB bootstrap, migrations, and seed scripts
│   ├── init_db.py         # Schema creation and admin seeding
│   ├── seed_product_db.py # Product ingredient knowledge base seeds
│   └── trustlens.db       # SQLite database (auto-created)
├── docs/                  # Detailed documentation
│   ├── GETTING_STARTED_AND_SPECIFICATIONS.md
│   ├── ARCHITECTURE.md
│   └── superpowers/       # Design specs & execution plans
├── models/                # SQLAlchemy database models
│   ├── user.py            # User and admin accounts
│   ├── scan.py            # Scan records
│   ├── product_db.py      # Product ingredient knowledge base
│   ├── report.py          # Community scam reports
│   └── support.py         # Support tickets and messages
├── routes/                # Flask Blueprints
│   ├── main.py            # Homepage, about, awareness, product/claim routes
│   ├── auth.py            # Authentication routes (login, register, logout)
│   ├── scanners.py        # 6 core scanner routes and JSON APIs
│   ├── dashboard.py       # User dashboard views
│   ├── reports.py         # Scam report portal
│   └── admin.py           # Admin panel and analytics endpoints
├── services/              # Heuristic scanning and forensic engines
│   ├── website_scanner.py
│   ├── email_scanner.py
│   ├── job_scanner.py
│   ├── whatsapp_scanner.py
│   ├── qr_scanner.py
│   ├── payment_scanner.py
│   ├── product_scanner.py
│   ├── claim_scanner.py
│   ├── scoring.py
│   └── analytics.py
├── static/                # Static assets (CSS, JS, images, icons)
│   ├── css/style.css      # Editorial design system stylesheet
│   └── js/main.js         # Interactive client logic, drop zones, gauges
├── templates/             # Jinja2 HTML templates
│   ├── base.html          # Global shell with navigation and theme toggle
│   ├── index.html         # Homepage showcase
│   ├── scanners/          # Scanner interface templates
│   ├── admin/             # Admin dashboard and analytics
│   └── components/        # Reusable macros (icons.html)
└── tests/                 # Automated test suites
```

---

## License

MIT License. Free for educational, research, and non-commercial use.
