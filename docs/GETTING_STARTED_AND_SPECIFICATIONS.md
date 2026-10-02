# TrustLens — Project Guide & Specifications

Welcome to the comprehensive technical documentation for **TrustLens: AI-Based Information Verification System**. This document details how to set up, configure, and run the project, along with in-depth specifications for all 8 verification engines and platform features.

---

## Table of Contents

1. [System Overview & Architecture](#1-system-overview--architecture)
2. [Prerequisites & System Requirements](#2-prerequisites--system-requirements)
3. [Step-by-Step Setup & How to Run](#3-step-by-step-setup--how-to-run)
   - [macOS Port 5000 Conflict Notice](#important-macos-port-5000-conflict-notice)
   - [Running with SQLite (Default)](#running-with-sqlite-default)
   - [Running with MySQL (Optional)](#running-with-mysql-optional)
4. [Authentication & Default Admin Credentials](#4-authentication--default-admin-credentials)
5. [Specifications for All 8 Verification Engines](#5-specifications-for-all-8-verification-engines)
   - [1. Website Scanner](#1-website-scanner)
   - [2. Email Phishing Scanner](#2-email-phishing-scanner)
   - [3. Job & Internship Fraud Checker](#3-job--internship-fraud-checker)
   - [4. WhatsApp & Chat Screenshot Scanner](#4-whatsapp--chat-screenshot-scanner)
   - [5. QR Code Threat Scanner](#5-qr-code-threat-scanner)
   - [6. Payment Screenshot Forensics Analyzer](#6-payment-screenshot-forensics-analyzer)
   - [7. Product Ingredient Safety Scanner](#7-product-ingredient-safety-scanner)
   - [8. Truth & Rumor Claim Checker](#8-truth--rumor-claim-checker)
6. [Platform Features & Architecture](#6-platform-features--architecture)
   - [Editorial & Institutional UI with Dual-Theming](#editorial--institutional-ui-with-dual-theming)
   - [Explainable Circular Trust/Risk Gauges](#explainable-circular-trustrisk-gauges)
   - [Community Scam Reports Portal](#community-scam-reports-portal)
   - [Dynamic Blacklist Engine](#dynamic-blacklist-engine)
   - [Admin Analytics & Audit Dashboard](#admin-analytics--audit-dashboard)
   - [Automated Email Notifications (Flask-Mail)](#automated-email-notifications-flask-mail)
7. [API Endpoints Reference](#7-api-endpoints-reference)
8. [Testing & Quality Assurance](#8-testing--quality-assurance)
9. [Troubleshooting & FAQs](#9-troubleshooting--faqs)

---

## 1. System Overview & Architecture

TrustLens is a production-grade multi-vector fraud and misinformation detection platform. Unlike single-purpose scam detectors, TrustLens provides 8 specialized heuristic engines spanning URLs, emails, employment offers, chat screenshots, QR payloads, financial receipts, consumer ingredient labels, and factual claims.

### Key Architectural Characteristics
- **Monolithic MVC Architecture**: Built on **Flask 3.x** and **SQLAlchemy 2.x**.
- **Deterministic Heuristics Engine**: Replaces non-deterministic black-box scores with transparent, check-by-check penalty and reward attribution (0–100 scale).
- **Computer Vision & OCR Pipeline**: Integrates **EasyOCR**, **OpenCV**, **Pillow**, and **NumPy** for forensic analysis of chat logs, receipts, and product labels.
- **Institutional Editorial UI**: Designed with a high-trust, monochrome aesthetic inspired by Linear, Stripe Press, and Vercel, with native anti-FOUC dual-theming (light & dark).

---

## 2. Prerequisites & System Requirements

- **Python**: Version `3.10` or higher (Python 3.9–3.12 supported).
- **Package Manager**: `pip` (Python package manager).
- **Operating Systems**: macOS, Linux (Ubuntu/Debian/Fedora), or Windows 10/11.
- **Native Libraries (Optional)**:
  - `libzbar` (optional for native QR decoding; if absent, the system seamlessly falls back to OpenCV and ZXing-CPP).

---

## 3. Step-by-Step Setup & How to Run

### Step 1: Clone or Navigate to the Project

```bash
cd /path/to/trustlens-fresh
```

### Step 2: Create and Activate a Python Virtual Environment

It is recommended to run TrustLens in an isolated virtual environment:

**On macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**On Windows (Command Prompt / PowerShell):**
```cmd
python -m venv .venv
.venv\Scripts\activate
```

### Step 3: Install Required Dependencies

```bash
pip install -r requirements.txt
```

> **Note on OCR Models:** On first run of image-based scanners (WhatsApp, Payment, Product), `EasyOCR` will automatically download lightweight text recognition model weights (~80MB).

### Step 4: Configure Environment Variables

Copy the example environment configuration:

```bash
cp .env.example .env
```

Review or modify `.env` as needed:
```ini
# Flask Secret Key
SECRET_KEY=replace-with-a-secure-random-string

# Database Mode (0 = SQLite, 1 = MySQL)
USE_MYSQL=0

# Bootstrap Administrator
ADMIN_EMAIL=gunjbazaz143@gmail.com
ADMIN_PASSWORD=Admin@12345

# Email Alert Configuration (Optional)
MAIL_ALERT_RECIPIENT=gunjbazaz143@gmail.com
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_USE_TLS=1
```

---

### IMPORTANT: macOS Port 5000 Conflict Notice

> [!WARNING]
> On macOS (Monterey, Ventura, Sonoma, Sequoia), **AirPlay Receiver** listens on port `5000` by default (`ControlCenter`). Running Flask on port `5000` will result in `403 Forbidden` or `Port 5000 not allowed for HTTP`.
> 
> **Always run TrustLens on port `5001` or another open port on macOS!**

---

### Step 5: Launch the Application

#### Option A: Running Development Server on Port 5001 (Recommended for macOS)

```bash
PORT=5001 python run.py
```
Or with custom environment variables:
```bash
PORT=5001 python app.py
```

#### Option B: Standard Launch (Default Port 5000)

```bash
python run.py
```

Once started, open your web browser and navigate to:
- **Local URL:** [http://127.0.0.1:5001](http://127.0.0.1:5001) (or `http://127.0.0.1:5000`)

---

### Running with MySQL (Optional)

TrustLens defaults to zero-config **SQLite** located at `database/trustlens.db`. To run with **MySQL**:

1. Start your MySQL service (e.g. via XAMPP, Homebrew, or Docker).
2. Create an empty database:
   ```sql
   CREATE DATABASE trustlens CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
3. Update `.env`:
   ```ini
   USE_MYSQL=1
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=your_password
   DB_NAME=trustlens
   ```
4. Run `python run.py`. Database tables, initial admin credentials, and product knowledge base records are automatically provisioned on boot.

---

## 4. Authentication & Default Admin Credentials

TrustLens automatically bootstraps the official administrator on initial launch:

| Attribute | Default Value | Notes |
| :--- | :--- | :--- |
| **Admin Email** | `gunjbazaz143@gmail.com` | Official admin account |
| **Fallback Email** | `admin@trustlens.io` | Secondary fallback admin |
| **Default Password** | `Admin@12345` | Set in `.env` / `database/init_db.py` |
| **Admin Portal** | `/admin` | Accessible only to users with `is_admin=True` |

To create regular user accounts, navigate to `/auth/register` or click **Get Started** in the top navigation bar.

---

## 5. Specifications for All 8 Verification Engines

TrustLens computes explainable trust scores on a **0 to 100** scale:
- **Safe (70 – 100)**: Clean heuristics, valid security protocols, low fraud probability.
- **Warning / Suspicious (45 – 69)**: Multiple flags, atypical patterns, or urgency manipulation.
- **Dangerous (0 – 44)**: Confirmed threat markers, blacklisted domains, or fraudulent credentials.

---

### 1. Website Scanner
- **Endpoint**: `/website-scanner` | API: `POST /api/scan/website`
- **Purpose**: Detects phishing websites, lookalike domains, fake login pages, and rogue servers.
- **Inspection Rules (31 Checks)**:
  - Protocol verification (enforced HTTPS, TLS/SSL certificate validity).
  - Domain age, registration tenure, and TLD reputation (`.xyz`, `.top`, `.tk`, etc.).
  - Suspicious keywords (`login`, `secure`, `verify`, `banking`, `update-account`).
  - IP hostnames, hidden port usage, and multi-hop redirect chains.
  - Presence in the local administrator threat blacklist.

### 2. Email Phishing Scanner
- **Endpoint**: `/email-scanner` | API: `POST /api/scan/email`
- **Purpose**: Uncovers corporate impersonation, spear-phishing, credential harvesters, and advance-fee fraud.
- **Inspection Rules**:
  - Sender authenticity, domain mismatch, free-mail address spoofing (e.g., HR using `@gmail.com`).
  - Extracted links compared against threat patterns and shortened URL hubs.
  - Urgency indicators (e.g., "account suspended within 24 hours", "immediate action required").
  - Financial solicitation, wire transfer requests, and synthetic greeting signatures.

### 3. Job & Internship Fraud Checker
- **Endpoint**: `/job-checker` | API: `POST /api/scan/job`
- **Purpose**: Protects students and jobseekers from fake employment scams, recruitment fees, and identity theft.
- **Inspection Rules**:
  - Detection of illegal upfront onboarding/equipment/training fee requests.
  - Vague job responsibilities paired with unrealistic salary offerings.
  - Interview requests via Telegram, WhatsApp, or unsecured personal messaging.
  - Recruiter domain cross-checking against official corporate registries.

### 4. WhatsApp & Chat Screenshot Scanner
- **Endpoint**: `/whatsapp-scanner` | API: `POST /api/scan/whatsapp`
- **Purpose**: Optical Character Recognition (OCR) scanner designed to expose chat-based financial extortion, lottery scams, courier package hold-ups, and OTP theft.
- **Inspection Rules**:
  - Multi-language OCR extraction powered by EasyOCR.
  - Categorization into 6 threat categories: Lottery, OTP/KYC, Customs/Courier, Part-Time Job, Crypto/Investment, and Impersonation.
  - Extraction and threat analysis of phone numbers, UPI handles, and embedded hyperlinks.

### 5. QR Code Threat Scanner
- **Endpoint**: `/qr-scanner` | API: `POST /api/scan/qr`
- **Purpose**: Decodes physical and digital QR codes to detect malicious redirect links, payment hijacking, and drive-by malware downloads.
- **Inspection Rules**:
  - Multi-engine payload decoding: `zxing-cpp`, `pyzbar`, and `OpenCV`.
  - Destination URL extraction and automated evaluation via the Website Scanner engine.
  - Detection of malicious APK/app download triggers and embedded payment commands (`upi://`).

### 6. Payment Screenshot Forensics Analyzer
- **Endpoint**: `/payment-analyzer` | API: `POST /api/scan/payment`
- **Purpose**: Forensic verification of UPI payment confirmations (Google Pay, PhonePe, Paytm, Banking receipts) to prevent fake payment scams during deliveries and service transactions.
- **Inspection Rules**:
  - OCR extraction of UTR / Transaction IDs, timestamps, sender/receiver VPA, and amounts.
  - Font inconsistency, pixel anomaly, and compression artifact detection (identifying edited text in payment amounts).
  - Validation of transaction ID format against banking standards.

### 7. Product Ingredient Safety Scanner
- **Endpoint**: `/product-scanner` | API: `POST /api/scan/product`
- **Purpose**: Evaluates food, cosmetic, and pharmaceutical ingredient labels against reference safety databases to expose counterfeit goods, harmful additives, and banned chemicals.
- **Inspection Rules**:
  - OCR extraction of label ingredient statements.
  - Matching against 142+ curated toxicological ingredients and 27+ registered product records in the TrustLens database.
  - Identification of carcinogens, endocrine disruptors, allergens, and unregulated chemical substitutes.

### 8. Truth & Rumor Claim Checker
- **Endpoint**: `/claim-checker` | API: `POST /api/scan/claim`
- **Purpose**: Evaluates viral social media rumors, news headlines, and questionable factual statements.
- **Inspection Rules**:
  - Heuristic analysis of sensationalist keywords, conspiracy rhetoric, and emotional manipulation.
  - Authoritative reference checks and factual consistency cross-referencing.
  - Generates clear verdict levels: `VERIFIED AUTHENTIC`, `QUESTIONABLE / UNVERIFIED`, or `FALSE / DEBUNKED`.

---

## 6. Platform Features & Architecture

### Editorial & Institutional UI with Dual-Theming
- **Monochrome Foundation**: Built with a strict two-tone neutral palette (`#fbfbfb`/`#ffffff` in light mode, `#09090b`/`#121215` in dark mode) and single obsidian accent (`#0f172a`/`#f4f4f5`).
- **Anti-FOUC Native Switching**: Instant theme initialization in `<head>` honoring user preference (`localStorage`), system preference (`prefers-color-scheme`), and URL query parameters (`?theme=light` / `?theme=dark`).

### Explainable Circular Trust/Risk Gauges
- Enforced `aspect-ratio: 1 / 1; flex-shrink: 0;` CSS properties to ensure score gauges maintain perfect circular geometry without oval distortion.
- Subdued, institutional signal colors strictly reserved for final verdict states (`--signal-safe`, `--signal-warning`, `--signal-danger`).

### Community Scam Reports Portal
- Public portal (`/scam-reports`) allowing users to report new scams, upload evidence, and browse verified community warnings.
- Administrative approval workflow (`/admin/reports`) before community submissions appear publicly.

### Dynamic Blacklist Engine
- Admins can add malicious domains, phone numbers, or UPI IDs via `/admin/blacklist`.
- Any scanner encountering a blacklisted entity immediately marks the scan with 0 trust and displays a prominent warning banner.

### Admin Analytics & Audit Dashboard
- Comprehensive metrics portal (`/admin` and `/admin/analytics`):
  - 14-day scan volume line chart.
  - Risk distribution doughnut chart.
  - Ranked fraud type frequency bar chart.
  - User registration growth trends.
- Responsive Chart.js integration dynamically adapting gridlines and doughnut borders in real-time on theme toggles.

### Automated Email Notifications (Flask-Mail)
- Dispatches alert emails to administrators when critical scam reports or contact inquiries are submitted.
- Safe asynchronous fallback: if SMTP is unconfigured, submissions are stored in the database without disrupting user operations.

---

## 7. API Endpoints Reference

All scanner APIs return structured JSON payloads:

| Route | Method | Payload / Form Data | Response Structure |
| :--- | :--- | :--- | :--- |
| `/api/scan/website` | `POST` | `{"url": "https://..."}` | `{"score": 85, "risk_label": "Safe", "checks": [...]}` |
| `/api/scan/email` | `POST` | `{"email_text": "..."}` | `{"score": 42, "risk_label": "Dangerous", "checks": [...]}` |
| `/api/scan/job` | `POST` | `{"job_text": "..."}` | `{"score": 35, "risk_label": "Dangerous", "checks": [...]}` |
| `/api/scan/whatsapp` | `POST` | `multipart/form-data` (`image`) | `{"score": 25, "category": "Lottery", "checks": [...]}` |
| `/api/scan/qr` | `POST` | `multipart/form-data` (`image`) | `{"score": 50, "payload": "...", "checks": [...]}` |
| `/api/scan/payment` | `POST` | `multipart/form-data` (`image`) | `{"score": 30, "utr": "...", "checks": [...]}` |
| `/api/scan/product` | `POST` | `multipart/form-data` or JSON | `{"score": 75, "ingredients": [...], "status": "..."}` |
| `/api/scan/claim` | `POST` | `{"claim_text": "..."}` | `{"score": 60, "verdict": "Unverified", "confidence": "..."}` |
| `/admin/api/analytics` | `GET` | *Session cookie (Admin only)* | `{"scan_volume": [...], "risk": {...}, "fraud_types": [...]}` |

---

## 8. Testing & Quality Assurance

TrustLens contains an automated unit test suite verifying scanner logic, database operations, and authentication.

To run the complete test suite:

```bash
# Ensure virtual environment is active
source .venv/bin/activate

# Execute all tests
python -m unittest discover tests/
```

To run a specific scanner test:
```bash
python -m unittest tests/test_website_scanner.py
python -m unittest tests/test_email_scanner.py
python -m unittest tests/test_claim_scanner.py
python -m unittest tests/test_product_scanner.py
```

Expected output:
```
Ran 20 tests in ~7.0s
OK
```

---

## 9. Troubleshooting & FAQs

### Q: Why do I get "403 Forbidden" or "Port not allowed" when running on port 5000?
**A:** macOS AirPlay Receiver uses port `5000`. Launch the server using:
```bash
PORT=5001 python run.py
```

### Q: `ImportError: Unable to find zbar shared library` appears in test logs.
**A:** `pyzbar` looks for native C libraries for barcode reading. TrustLens includes automated fallbacks to **ZXing-CPP** and **OpenCV**, so QR scanning continues to function seamlessly even without native `zbar` installed.

### Q: How do I change the default admin password?
**A:** Either modify `ADMIN_PASSWORD` in your `.env` file before initial boot, or log into `/admin` and update administrator account credentials in the settings view.

### Q: How do I test light mode vs dark mode?
**A:** Click the theme toggle icon (Sun/Moon) in the top navbar, or append `?theme=light` or `?theme=dark` directly to any URL in your browser.
