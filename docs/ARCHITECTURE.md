# TrustLens Architecture & System Overview

## 1. Architecture Overview
TrustLens is built on a monolithic **Flask**-based architecture utilizing a Model-View-Controller (MVC) pattern adapted for information verification and scanning:
* **Models (`models/`):** Defines data models and schemas via **Flask-SQLAlchemy** for users, scan reports, product knowledge base items, and admin configurations.
* **Views / Front-end (`templates/`, `static/`):** Renders server-side templates using Jinja2 along with client-side CSS, JavaScript, and asset files.
* **Controllers / Routes (`routes/`):** Modular request handlers divided into Flask Blueprints handling authentication, administrative tasks, dashboards, reporting, and scanning actions.
* **Services / Business Logic (`services/`):** The core intelligence and verification pipeline containing modular scanner engines (e.g., QR, website, email, payment, product, WhatsApp, and claim verification).

---

## 2. Dependencies
Key dependencies defined in `requirements.txt`:
* **Web Framework & Authentication:**
  * `Flask` (>=3.0.0)
  * `Flask-SQLAlchemy` (>=3.1.1)
  * `Flask-Login` (>=0.6.3)
  * `Werkzeug` (>=3.0.0)
* **Database & Persistence:**
  * `PyMySQL` (>=1.1.0)
  * `cryptography` (>=41.0.0)
* **Configuration:**
  * `python-dotenv` (>=1.0.0)
* **Image Processing & OCR:**
  * `Pillow` (>=10.1.0)
  * `opencv-python-headless` (>=4.9.0)
  * `easyocr` (>=1.7.1)
  * `numpy` (>=1.26.0)
* **QR Decoding & Generation:**
  * `pyzbar` (>=0.1.9)
  * `zxing-cpp` (>=2.2.0)
  * `qrcode` (>=7.4.2)
* **Networking, Parsing & Validation:**
  * `requests` (>=2.31.0)
  * `validators` (>=0.22.0)
  * `python-multipart` (>=0.0.6)
* **Email & Notifications:**
  * `Flask-Mail` (>=0.9.1)

---

## 3. Directory Structure
```
trustlens-fresh/
├── app_factory.py         # Application factory (Flask configuration, extensions, blueprints, error handlers)
├── app.py                 # Alternative/standard WSGI entry point
├── run.py                 # Local development server launcher
├── config.py              # Configuration classes and environment variable handling
├── .env.example           # Example environment variable configuration
├── requirements.txt       # Project dependencies
├── database/              # DB setup, schema creation, and database seed scripts
│   ├── init_db.py         # Table initialization and default admin seeding
│   └── seed_product_db.py # Product knowledge base seeding script
├── models/                # SQLAlchemy database models
│   ├── __init__.py        # Database instance and model exports
│   ├── user.py            # User account model
│   ├── admin.py           # Admin settings and logs
│   ├── scan.py            # Scan records and results
│   ├── product_db.py      # Product records database
│   ├── product_candidate.py
│   ├── report.py          # User feedback and reports
│   └── support.py         # Support ticket entities
├── routes/                # Route definitions structured as Flask Blueprints
│   ├── __init__.py        # Blueprint registration helper
│   ├── auth.py            # User authentication (login, register, logout)
│   ├── admin.py           # Admin panel endpoints
│   ├── dashboard.py       # User dashboard views
│   ├── main.py            # Core landing pages and navigation
│   ├── reports.py         # Scan report inspection and generation
│   └── scanners.py        # Verification and scanning API endpoints
├── services/              # Core domain services and scanner modules
│   ├── __init__.py        # Service exports
│   ├── qr_scanner.py      # QR code detection and URL analysis
│   ├── website_scanner.py # Domain, SSL, and web content checks
│   ├── email_scanner.py   # Phishing, SPF/DKIM verification, and email header analysis
│   ├── payment_scanner.py # UPI, payment gateway, and fraudulent transaction detection
│   ├── payment_forensics.py
│   ├── product_scanner.py # Fake product detection and validation
│   ├── product_knowledge_base.py
│   ├── claim_scanner.py   # Information claim and fact-checking logic
│   ├── job_scanner.py     # Job offer fraud detection
│   ├── whatsapp_scanner.py# WhatsApp message and link verification
│   ├── analytics.py       # Metrics and analytics aggregation
│   ├── scoring.py         # Risk scoring engines
│   ├── mail.py            # Email dispatch utilities
│   └── logger.py          # Operational logging helpers
├── static/                # Static assets (CSS, JS, images, vendor libraries)
├── templates/             # Jinja2 HTML templates
│   ├── 404.html
│   ├── 500.html
│   └── ...                # Feature-specific page templates
├── tests/                 # Test suites
└── docs/                  # Project documentation
```

---

## 4. Entry Points
* **`run.py`**: Primary development entry point (`python run.py`). Instantiates the application with `create_app()` and launches the Flask development server on `127.0.0.1:5000` with debug mode enabled.
* **`app_factory.py`**: Implements the Application Factory pattern (`create_app(config_class=Config)`). Responsible for:
  1. Initializing core Flask app instance.
  2. Loading configuration from `config.py`.
  3. Initializing Flask extensions (`SQLAlchemy`, `Flask-Login`).
  4. Setting up user loader callbacks for session authentication.
  5. Initializing database schema (`database.init_db.init_app`).
  6. Registering all modular blueprints from `routes/`.
  7. Registering custom HTTP error handlers (404, 500, 413).
  8. Injecting template context globals.

---

## 5. State Management & API Design
### State Management
* **Persistent State:**
  * Backed by a relational database (MySQL/PyMySQL or SQLite fallback depending on `config.py`).
  * Managed via **Flask-SQLAlchemy** (`models.db`). The session lifecycle is tied to request contexts and transactions within service modules.
* **User & Session State:**
  * Handled via **Flask-Login** using encrypted client-side session cookies.
  * User lookups are performed dynamically on each request via `@login_manager.user_loader` querying `models.user.User`.
  * Access control enforced using the `@login_required` decorator across protected routes.

### API & Routing Management
* **Modular Blueprints:** Routes are decoupled into dedicated blueprints under `routes/` (e.g., `auth_bp`, `admin_bp`, `scanners_bp`).
* **Registration:** All blueprints are registered in `routes/__init__.py` through `register_blueprints(app)`, which maps each module cleanly under corresponding URL prefixes.
* **Hybrid View/API Endpoints:** The route controllers handle both HTML page rendering (for user-facing workflows) and JSON request/response processing (for AJAX/scanner APIs that return analysis results and risk scores).

