# TrustLens Codebase Remediation Specification

**Date:** 2026-09-24  
**Status:** Draft / Pending Review  
**Topic:** Comprehensive Resolution of Issues Identified in Codebase Audits (`docs/ISSUES_AUDIT.md` & `docs/CODEBASE_AUDIT_AND_ROADMAP.md`)  
**Scope:** Architectural Remediation across Core, Routes, Services, Database, and Models  

---

## 1. Problem Statement & Scope

A comprehensive audit of the TrustLens repository identified 18 verified issues categorized into Critical, Medium, and Low severity. These issues span critical data-loss hazards (auto-dropping production tables), severe logic contradictions (email scanner inverting trust scores), critical security vulnerabilities (SSRF, zero CSRF protection, open redirect, state-mutating GET endpoints), worker thread resource exhaustion (EasyOCR timeouts), and performance bottlenecks ($N+1$ query multiplication).

This specification details the architectural redesign, interface contracts, and implementation changes required to resolve all identified issues without breaking existing legitimate scanning functionality.

---

## 2. Architectural Decisions & Remediation Modules

The remediation is organized into four core modules:

```
┌────────────────────────────────────────────────────────────────────────┐
│                      REMEDIATION ARCHITECTURE                          │
├─────────────────────────┬──────────────────────────────────────────────┤
│ Module                  │ Target Areas                                 │
├─────────────────────────┼──────────────────────────────────────────────┤
│ 1. Security Hardening   │ CSRF Protection, SSRF Guard, Open Redirect,  │
│                         │ GET Mutation Elimination, Upload Validation   │
├─────────────────────────┼──────────────────────────────────────────────┤
│ 2. Data Safety & DB     │ Auto-Drop Removal, Safe URI Parsing,         │
│                         │ Transaction Rollbacks, SQLite Cascades       │
├─────────────────────────┼──────────────────────────────────────────────┤
│ 3. Logic & Flow Fixes   │ Email Scoring Normalization, EasyOCR Timeout │
│                         │ Unblock, Non-QR Classification, Dashboard IDP│
├─────────────────────────┼──────────────────────────────────────────────┤
│ 4. Query Optimization   │ Analytics Grouping, Indexed Lookup,          │
│                         │ Unified Dashboard Scan History               │
└─────────────────────────┴──────────────────────────────────────────────┘
```

---

### Module 1: Security Hardening

#### 1.1 CSRF Protection
* **Files**: `requirements.txt`, `app_factory.py`, `templates/` (forms and AJAX headers).
* **Changes**:
  * Add `Flask-WTF>=1.2.1` to `requirements.txt`.
  * Initialize `csrf = CSRFProtect(app)` in `app_factory.py`.
  * Inject CSRF token meta tag (`<meta name="csrf-token" content="{{ csrf_token() }}">`) in `templates/base.html`.
  * Configure `TrustLens.apiPost` in `static/js/main.js` to automatically attach `X-CSRFToken` from the meta tag to all AJAX POST requests.
  * Exempt public scanner API endpoints (`/api/scan-*`, `/api/submit-report`) if intended for machine/external consumption, or configure client-side token inclusion.

#### 1.2 State Mutation Elimination on HTTP GET
* **Files**: `routes/admin.py`, `templates/admin/blacklist.html`, `templates/admin/messages.html`.
* **Changes**:
  * Change `@admin_bp.route("/blacklist/<int:domain_id>/delete")` to `methods=["POST"]`. Update the admin blacklist template to use a small POST form with CSRF token instead of an `<a href>` link.
  * Change `@admin_bp.route("/messages/<int:msg_id>/read")` to `methods=["POST"]`. Update the admin messages template accordingly.

#### 1.3 Server-Side Request Forgery (SSRF) Guard & Byte Streaming
* **Files**: `services/network_security.py` (new), `services/website_scanner.py`, `services/job_scanner.py`.
* **Changes**:
  * Create `services/network_security.py` providing `validate_public_url(url: str) -> tuple[bool, str]`:
    1. Parse URL with `urllib.parse.urlsplit` (reject non-HTTP/HTTPS schemes).
    2. Resolve DNS hostname via `socket.getaddrinfo()`.
    3. Validate each resolved IP address using Python's `ipaddress` library: ensure `not (ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast)`.
  * In `website_scanner._tls_probe` and `_fetch_page`, invoke `validate_public_url()` prior to socket creation or HTTP requests.
  * In `website_scanner._fetch_page`, configure `requests.get` with `stream=True` and read up to `MAX_FETCH_BYTES = 2 * 1024 * 1024` (2 MB). Discard further content to prevent memory exhaustion (OOM).
  * In `job_scanner._probe`, validate target website domain using `validate_public_url()` before dispatch.

#### 1.4 Open Redirect Sanitization in Authentication
* **Files**: `routes/auth.py`.
* **Changes**:
  * In `routes/auth.py:login()`, inspect `next_page = request.args.get("next")`.
  * Verify that `urlsplit(next_page).netloc == ""` and `not next_page.startswith("//")` and `next_page.startswith("/")`.
  * If invalid or external, discard and redirect safely to `url_for("dashboard.index")`.

#### 1.5 Secure File Upload Verification in Scam Reports
* **Files**: `routes/reports.py`.
* **Changes**:
  * Apply `_verify_image_file()` from `routes/scanners.py` to `routes/reports.py:submit_report()`.
  * Reject non-image or corrupted files using Pillow's `Image.open().verify()` and enforce `MAX_CONTENT_LENGTH` checks before saving.

---

### Module 2: Data Safety & Schema Integrity

#### 2.1 Elimination of Destructive Auto-Drop
* **Files**: `database/init_db.py`.
* **Changes**:
  * Remove `_drop_table()` call from `_verify_schema()`.
  * When `removed` columns exist (columns present in the database but absent in the model), log an explicit warning with instructions for manual migration, preserving all table data:
    ```python
    if added and not removed:
        _add_missing_columns(app, table, added)
    elif removed:
        app.logger.warning("Table '%s' contains columns not in model: %s. Preserving existing data.", table.name, removed)
    ```

#### 2.2 Robust Database Connection URI Parsing
* **Files**: `database/init_db.py`.
* **Changes**:
  * Replace naive `.split()` operations in `_ensure_database()` with SQLAlchemy's `make_url(uri)`.
  * Safely extract `url.host`, `url.port`, `url.username`, `url.password`, and `url.database` without breaking on special characters (`@`, `:`) or query parameters.

#### 2.3 Transaction Rollbacks on Admin Route Mutations
* **Files**: `routes/admin.py`.
* **Changes**:
  * Wrap all database write routines (`product_new`, `product_edit`, `product_delete`, `ingredient_add`, `ingredient_delete`, `category_add`, `category_delete`, `blacklist_add`, `blacklist_delete`) in structured `try...except Exception:` blocks.
  * Ensure `db.session.rollback()` is invoked on any exception, logging the traceback and returning an informative flash message to the administrator.

#### 2.4 Product ID Generation Concurrency Protection
* **Files**: `routes/admin.py`.
* **Changes**:
  * In `_generate_product_id()`, incorporate a random 6-character hex token (`uuid.uuid4().hex[:6]`) into the candidate ID.
  * Wrap insertion in collision-handling retry logic to eliminate race-condition `IntegrityError` failures.

#### 2.5 SQLite Foreign Key Cascades & Cleanup
* **Files**: `models/product_db.py`.
* **Changes**:
  * Add `cascade="all, delete-orphan"` to `Product` model relationships (`identifiers`, `images`, `attributes`, `verifications`, `score_factors`).
  * Ensure SQLite connections execute `PRAGMA foreign_keys = ON;` upon connection if SQLite dialect is detected.

---

### Module 3: Logic & Flow Correctness

#### 3.1 Normalization of Email Scoring Semantics
* **Files**: `services/email_scanner.py`, `models/scan.py`, `tests/test_email_scanner.py`.
* **Changes**:
  * Align `services/email_scanner.py` with `services/scoring.py` and the other 7 scanners:
    * Compute `trust_score = max(0, min(100, 100 - risk))`.
    * Return `"score": trust_score` and `"risk_score": risk`.
  * Ensure `persist_scan()` stores the normalized `trust_score` in `EmailScan.trust_score`.
  * In `templates/scanners/email_scanner.html`, display the primary score using `TrustLens.renderGauge` (Trust Score) with a secondary risk breakdown, or pass `risk_score` to `renderRiskGauge` so the UI and database remain coherent.
  * Update `tests/test_email_scanner.py` to assert against `trust_score` or test `risk_score` explicitly.

#### 3.2 EasyOCR Thread Pool Timeout Unblocking
* **Files**: `services/whatsapp_scanner.py`.
* **Changes**:
  * Refactor `extract_text_ocr()` to manage the `ThreadPoolExecutor` lifecycle explicitly without the `with` context manager:
    ```python
    pool = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    try:
        future = pool.submit(reader.readtext, image_path, detail=0, paragraph=True)
        lines = future.result(timeout=Config.OCR_TIMEOUT_SECONDS)
        pool.shutdown(wait=False)
        return "\n".join(str(line).strip() for line in lines if str(line).strip())
    except concurrent.futures.TimeoutError:
        pool.shutdown(wait=False, cancel_futures=True)
        logger.warning("OCR timed out for %s", image_path)
        return ""
    except Exception:
        pool.shutdown(wait=False)
        logger.exception("OCR failed for %s", image_path)
        return ""
    ```

#### 3.3 Accurate Non-QR Image Classification
* **Files**: `services/qr_scanner.py`.
* **Changes**:
  * When no QR code is detected in `scan_qr_image()`, do not classify the result as `status="dangerous"` with `score=0`.
  * Return `status="warning"` or `status="unverifiable"` with `score=50`, and a clear neutral verdict `"No QR Code Detected"`.
  * Update `persist_scan()` to record the unverifiable status without incrementing `dangerous_scans` counters.

#### 3.4 Idempotent Dashboard Notification State
* **Files**: `routes/dashboard.py`.
* **Changes**:
  * Remove `reply.is_viewed = True` mutation from `GET /dashboard`.
  * Introduce an explicit `POST /api/reports/<int:report_id>/mark-viewed` endpoint called asynchronously when the user views the report details or clicks to acknowledge updates.

---

### Module 4: Performance & Extensibility

#### 4.1 Analytics Aggregation via SQL Group By
* **Files**: `services/analytics.py`.
* **Changes**:
  * Replace the 112-query loop in `scan_volume_timeseries()` with single aggregation queries using `db.func.date(m.created_at)` grouped by date for each model (or consolidated scan query).
  * Replace the in-memory row iteration in `fraud_type_counts()` with SQL grouping:
    ```python
    rows = (
        db.session.query(ScamReport.scam_type, db.func.count(ScamReport.id))
        .group_by(ScamReport.scam_type)
        .all()
    )
    ```

#### 4.2 In-Memory Ingredient Lookup Optimization
* **Files**: `routes/admin.py`.
* **Changes**:
  * In `_resolve_ingredient(name: str)`, replace `for ing in Ingredient.query.all():` with an indexed database query matching `normalized_name`:
    ```python
    target = _norm(name)
    ing = Ingredient.query.filter_by(normalized_name=target).first()
    if not ing:
        # Fall back to JSON alias search or indexed alias lookup
        ...
    ```

#### 4.3 Unified Dashboard Scan Feed
* **Files**: `routes/dashboard.py`, `templates/dashboard.html`.
* **Changes**:
  * Aggregate recent scans across all 8 scanner models (`WebsiteScan`, `EmailScan`, `QRScan`, `PaymentScan`, `JobScan`, `ProductScan`, `WhatsAppScan`, `ClaimScan`) ordered by `created_at DESC` limited to 10 entries.
  * Render scan type badges, target identifiers, trust scores, and status pills in the dashboard recent scans table.

---

## 3. Verification & Testing Strategy

1. **Unit & Regression Testing**:
   * Run existing scanner regression test suites (`python tests/test_claim_scanner.py`, `python tests/test_email_scanner.py`, etc.) ensuring all evidence algorithms produce expected classifications.
   * Add dedicated test cases in `tests/test_security_remediation.py`:
     * SSRF guard blocks `127.0.0.1`, `localhost`, `169.254.169.254`, `10.0.0.1`, and resolves public domains properly.
     * Open redirect validation rejects external domains and accepts relative paths.
     * CSRF protection rejects state-changing POST requests lacking valid tokens.
     * Email scanner outputs consistent `score` (trust) and `risk_score` (risk).
     * EasyOCR unblocked timeout does not hang worker threads when timed out.
2. **Database Bootstrap Integrity Test**:
   * Verify startup initialization with SQLite and MySQL does not drop tables on drifted columns.
   * Verify admin password bootstrap and idempotent seeding functions survive restarts.
3. **Manual Flow Verification**:
   * Test web scan, email scan, QR scan, payment upload, report submission, and admin workflow via browser/API endpoints.

