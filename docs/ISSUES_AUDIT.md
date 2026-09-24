# TrustLens Code Quality & Logic Audit

## Executive Summary
This document provides an exhaustive, code-level quality, security, and logic audit of the TrustLens codebase. 

While the application features well-structured modular components (Flask Blueprints, SQLAlchemy models, and comprehensive heuristic analysis engines across multiple scan categories), several **critical failure points** and **architectural inconsistencies** threaten system stability, data integrity, and security:

1. **Catastrophic Auto-Drop Mechanism**: The database bootstrap routine silently drops live production tables upon schema drift, causing irreversible data loss.
2. **Inverted Score Definition in Email Scanner**: The email scanner measures *risk* (0=safe, 100=danger) while the rest of the ecosystem treats score as *trust* (100=safe, 0=danger), polluting `EmailScan.trust_score`, AI logs, and platform analytics.
3. **Server-Side Request Forgery (SSRF) & Uncapped Ingestion**: URL and job checking engines accept arbitrary URLs and probe internal addresses/metadata services without private IP validation or response payload limits.
4. **Zero CSRF Protection & Mutating GET Handlers**: No CSRF tokens exist anywhere in the application, and administrative deletions/status updates are exposed over unauthenticated/unprotected HTTP GET requests.
5. **Worker Thread Exhaustion in OCR**: The timeout implementation in `EasyOCR` text extraction fails to abort hanging worker threads due to Python's `ThreadPoolExecutor` context manager behavior.
6. **Severe Performance Bottlenecks**: The analytics and dashboard modules run hundreds of unindexed SQL queries per page load (e.g. 112 queries per 14-day scan volume chart).

---

## Critical / High Priority

### 1. Destructive Auto-Drop of Production Tables on Application Startup
* **Location**: `database/init_db.py:95`
* **Problem**: 
  In `_verify_schema()`, the codebase compares live database columns against SQLAlchemy model metadata. If a column is dropped, renamed, or drifted, the check `added and not removed` evaluates to `False`, immediately triggering `_drop_table(app, table.name)`. On the next application startup, live tables (including user accounts, scam reports, and scan histories) are dropped via `DROP TABLE IF EXISTS` without warning or backup.
* **Recommended Fix**:
  Remove automated table dropping from runtime initialization. Adopt proper migration tools like Alembic / Flask-Migrate, and limit runtime checks to safe, non-destructive alterations or warning logs:
  ```python
  # database/init_db.py
  if added and not removed:
      _add_missing_columns(app, table, added)
  elif removed:
      app.logger.warning(
          "Table '%s' has drifted columns (%s). Run migration script to reconcile.",
          table.name, removed
      )
  ```

### 2. Inverted Scoring Semantics in Email Scanner Corrupts Database and Analytics
* **Location**: `services/email_scanner.py:1287-1336` (and `tests/test_email_scanner.py:28-37`)
* **Problem**:
  Across all scanners (`scoring.py`, `website_scanner.py`, `job_scanner.py`, `qr_scanner.py`, `payment_scanner.py`), `score` represents **Trust Score** where `100` = Safe and `0` = Dangerous (`status = classify(score)`). In `email_scanner.py`, `score` is calculated as a **Risk Score** (where `0-20` is safe and `80-100` is dangerous). In `persist_scan()`, this is stored as:
  ```python
  scan = EmailScan(..., trust_score=payload["score"], status=payload["status"])
  ```
  Consequently, a completely safe email gets saved with a `trust_score` of `0` to `20`, and a phishing email gets saved with a `trust_score` of `80` to `100`. Furthermore, `log_scan()` logs this inverted metric into `ai_logs`, skewing analytics and reporting widgets across the dashboard.
* **Recommended Fix**:
  Normalize `email_scanner.py` to produce a trust score consistent with the rest of the application (or invert it when persisting to `EmailScan.trust_score` and `log_scan`):
  ```python
  # services/email_scanner.py
  trust_score = max(0, min(100, 100 - risk))
  result = {
      "score": trust_score,
      "risk_score": risk,
      "status": cat["status"],
      ...
  }
  ```

### 3. Server-Side Request Forgery (SSRF) and Uncapped Ingestion in Website and Job Scanners
* **Location**: `services/website_scanner.py:237`, `services/website_scanner.py:329-331`, `services/job_scanner.py:214-219`
* **Problem**:
  `scan_website()` and `scan_job()` accept arbitrary user-supplied URLs and immediately execute raw socket connections (`socket.create_connection`) and HTTP requests (`requests.get(..., allow_redirects=True)`). No IP validation is performed. An attacker can supply internal IPs (`127.0.0.1`, `10.0.0.0/8`, `192.168.0.0/16`) or cloud metadata endpoints (`http://169.254.169.254/latest/meta-data/`). In addition, `_fetch_page` reads `resp.content` without a byte cap, exposing the server to Out-Of-Memory (OOM) Denial of Service via large file downloads.
* **Recommended Fix**:
  Resolve the host's IP prior to connection and reject non-public IPs. Disable automatic redirects or validate each redirect target IP. Stream responses with a strict maximum byte limit:
  ```python
  import ipaddress, socket

  def is_safe_host(host: str) -> bool:
      try:
          ip = ipaddress.ip_address(socket.gethostbyname(host))
          return not (ip.is_private or ip.is_loopback or ip.is_link_local)
      except Exception:
          return False
  ```

### 4. Zero Cross-Site Request Forgery (CSRF) Protection and State Mutation on GET Endpoints
* **Location**: `app_factory.py:17-67`, `routes/admin.py:182-190`, `routes/admin.py:251-258`
* **Problem**:
  The entire application lacks CSRF token validation. Forms in `routes/auth.py`, `routes/admin.py`, and `routes/reports.py` do not generate or verify CSRF tokens. Worse, several state-modifying actions are implemented using HTTP GET routes:
  * `/admin/blacklist/<domain_id>/delete` (deletes a blacklisted domain on GET)
  * `/admin/messages/<msg_id>/read` (updates message read state on GET)
  An attacker can execute cross-origin requests (e.g. via `<img src="http://localhost:5000/admin/blacklist/1/delete">`) to alter database records when an authenticated admin views a third-party webpage.
* **Recommended Fix**:
  1. Install `Flask-WTF` and register `CSRFProtect(app)` in `app_factory.py`.
  2. Convert all state-changing GET endpoints to POST endpoints with CSRF token validation:
  ```python
  @admin_bp.route("/blacklist/<int:domain_id>/delete", methods=["POST"])
  @admin_required
  def blacklist_delete(domain_id):
      ...
  ```

### 5. Open Redirect Vulnerability in User Authentication Flow
* **Location**: `routes/auth.py:31-33`
* **Problem**:
  The login handler takes an unvalidated `next` parameter directly from query arguments and passes it to `redirect()`:
  ```python
  next_page = request.args.get("next")
  return redirect(next_page or url_for("dashboard.index"))
  ```
  An attacker can distribute links like `https://trustlens.io/auth/login?next=https://malicious-site.com` or `//malicious-site.com`, causing the victim to be silently redirected to a phishing clone immediately after authenticating.
* **Recommended Fix**:
  Validate that `next_page` is a relative URL belonging to the same host before redirecting:
  ```python
  from urllib.parse import urlsplit

  def is_safe_redirect(target):
      if not target:
          return False
      ref_url = urlsplit(request.host_url)
      test_url = urlsplit(target)
      return (test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc) or (not test_url.netloc and test_url.path.startswith('/'))

  # In routes/auth.py
  if next_page and not is_safe_redirect(next_page):
      next_page = None
  return redirect(next_page or url_for("dashboard.index"))
  ```

### 6. EasyOCR ThreadPoolExecutor Timeout Lockup (Worker Hang)
* **Location**: `services/whatsapp_scanner.py:86-89`
* **Problem**:
  `extract_text_ocr()` handles OCR execution via a context manager:
  ```python
  with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
      future = pool.submit(reader.readtext, image_path, detail=0, paragraph=True)
      lines = future.result(timeout=Config.OCR_TIMEOUT_SECONDS)
  ```
  When `future.result()` raises `TimeoutError`, the `with` statement calls `pool.shutdown(wait=True)`. This blocks the current thread until `reader.readtext` finishes processing, defeating the purpose of the timeout and hanging the Flask worker process during heavy image operations.
* **Recommended Fix**:
  Avoid using the context manager for shutdown if a timeout occurs; trigger an unblocked shutdown:
  ```python
  pool = concurrent.futures.ThreadPoolExecutor(max_workers=1)
  try:
      future = pool.submit(reader.readtext, image_path, detail=0, paragraph=True)
      lines = future.result(timeout=Config.OCR_TIMEOUT_SECONDS)
      pool.shutdown(wait=False)
      return "\n".join(...)
  except concurrent.futures.TimeoutError:
      pool.shutdown(wait=False, cancel_futures=True)
      logger.warning("OCR timed out for %s", image_path)
      return ""
  ```

---

## Medium Priority

### 7. Unverified File Uploads and MIME-Type Spoofing in Scam Reports
* **Location**: `routes/reports.py:47-56`
* **Problem**:
  In `submit_report()`, screenshots are validated solely using the filename extension (`file.filename.rsplit(".", 1)[-1].lower() in ALLOWED_IMAGE_EXTENSIONS`). Unlike `routes/scanners.py`, `_verify_image_file()` is omitted. An attacker can upload arbitrary non-image files (HTML containing script tags, polyglots, oversized blobs) disguised with `.png`, which are persisted to `static/uploads/screenshots/` and served via static URLs.
* **Recommended Fix**:
  Validate file contents using PIL `Image.open().verify()` and enforce file size checks before saving to disk.

### 8. Missing Transaction Rollbacks on Admin Mutations
* **Location**: `routes/admin.py:425-452`, `routes/admin.py:469-501`, `routes/admin.py:556-603`, `routes/admin.py:635-659`
* **Problem**:
  In `product_new`, `product_edit`, `ingredient_add`, and `category_add`, `db.session.commit()` is called without `try...except ... db.session.rollback()` wrappers. If a constraint fails (e.g. unique constraint violation on `category_name` or `uq_product_ingredient`), the error is unhandled, rendering a 500 error page and leaving the SQLAlchemy session dirty for subsequent operations.
* **Recommended Fix**:
  Wrap all database writes in `try...except` blocks that roll back the session and surface readable error messages to the admin:
  ```python
  try:
      db.session.commit()
      flash("Changes saved.", "success")
  except Exception as exc:
      db.session.rollback()
      logger.exception("Failed to save product")
      flash("Database error: could not save product.", "danger")
  ```

### 9. Race Condition in Product ID Generation
* **Location**: `routes/admin.py:388-396`
* **Problem**:
  `_generate_product_id()` executes `while db.session.get(Product, candidate):` to find an available candidate ID before inserting. Because this check is not locked or atomic, concurrent product additions with identical names will generate identical candidate keys, resulting in an unhandled `IntegrityError` when committing.
* **Recommended Fix**:
  Incorporate unique cryptographic components (e.g. `uuid.uuid4().hex[:6]`) or handle `IntegrityError` with retries.

### 10. Massive N+1 Query Multiplication in Analytics and Dashboard
* **Location**: `services/analytics.py:82-98`, `services/analytics.py:49-60`, `routes/dashboard.py:24-37`, `routes/admin.py:291-300`
* **Problem**:
  * `scan_volume_timeseries()` runs `8 models * 14 days = 112` separate `COUNT()` queries synchronously on every request to `/admin/api/analytics`.
  * `_counts()` in `dashboard.py` issues 18 individual SQL count queries on every dashboard page render.
  * `fraud_type_counts()` loads every single scam report from the database into memory: `for (label,) in db.session.query(ScamReport.scam_type).all(): _add(label)`.
  * `_resolve_ingredient()` calls `Ingredient.query.all()` on each ingredient parse, loading the entire ingredient table into memory repeatedly.
* **Recommended Fix**:
  * Use SQL `GROUP BY` aggregates over date ranges instead of looping queries over individual days.
  * Execute `db.session.query(ScamReport.scam_type, db.func.count(ScamReport.id)).group_by(ScamReport.scam_type)`.
  * Query `Ingredient` using indexed lookups (`normalized_name = :norm`).

### 11. Database Mutation on GET Request in Dashboard Route
* **Location**: `routes/dashboard.py:64-71`
* **Problem**:
  When a user views `/dashboard` (GET request), the code marks unviewed report replies as viewed:
  ```python
  for report in my_reports:
      for reply in report.replies:
          if not reply.is_viewed:
              reply.is_viewed = True
  db.session.commit()
  ```
  HTTP GET requests must be idempotent. Web crawlers, link unfurlers, or accidental browser refreshes permanently clear "new reply" notifications without user interaction.
* **Recommended Fix**:
  Update `is_viewed` through an explicit POST API when the user opens or views the specific report detail modal.

### 12. Non-QR Images Misclassified as Malicious
* **Location**: `services/qr_scanner.py:603-612`
* **Problem**:
  If an uploaded image does not contain a QR code (or the QR code cannot be decoded), `scan_qr_image()` returns:
  ```python
  return {
      "score": 0, "status": "dangerous",
      "verdict": "No QR Code Detected",
      ...
  }
  ```
  This is saved to the database as a "dangerous" scan, falsely inflating platform scam metrics and reporting unreadable images as critical cyber threats.
* **Recommended Fix**:
  Return a distinct status code or a neutral `status: "unverifiable"` / `error: "No QR code detected"`. Do not record benign unreadable images as dangerous threats.

### 13. Naive String Slicing of Database Connection Strings
* **Location**: `database/init_db.py:50-55`
* **Problem**:
  In `_ensure_database()`, the MySQL database URI is parsed using raw string splitting:
  ```python
  host_part = uri.split("@")[1].split("/")[0]
  user = uri.split("//")[1].split(":")[0]
  password = uri.split("//")[1].split(":")[1].split("@")[0]
  ```
  If the password contains an `@` symbol or `:`, or if URL query parameters (like SSL settings) are present, this raises `IndexError` or connects with corrupted credentials.
* **Recommended Fix**:
  Use `urllib.parse.urlsplit` or `sqlalchemy.engine.make_url(uri)` to extract connection parameters safely.

### 14. User Dashboard Ignores 7 out of 8 Scanner Models
* **Location**: `routes/dashboard.py:44-46`, `templates/dashboard.html:39-70`
* **Problem**:
  Although `counts.total_scans` aggregates scans across all 8 models (`WebsiteScan`, `JobScan`, `EmailScan`, `WhatsAppScan`, `QRScan`, `PaymentScan`, `ProductScan`, `ClaimScan`), the "Recent Scans" table queries only `WebsiteScan`. Users who run email, payment, job, or QR scans never see their results in their dashboard recent scan history.
* **Recommended Fix**:
  Unify recent scans into a combined activity log or provide tabbed views showing recent activity per scan category.

---

## Low Priority / Code Smell

### 15. Deprecated `datetime.utcnow` Usage
* **Location**: `models/user.py:24`, `models/scan.py:16`, `models/report.py:43`, `models/product_db.py:53`, `models/product_candidate.py:48`, `models/admin.py:19`
* **Problem**:
  `datetime.utcnow` is deprecated as of Python 3.12 and will be removed in future versions.
* **Recommended Fix**:
  Use `datetime.now(timezone.utc)` or explicit UTC timestamps.

### 16. Orphaned Files on Multi-Image Upload Failure
* **Location**: `routes/scanners.py:316-324`
* **Problem**:
  During multi-image product label uploads, images are written to `static/uploads/products/` sequentially. If image 2 fails verification or processing, image 1 remains stored on disk permanently with no reference in the database.
* **Recommended Fix**:
  Verify images in-memory via stream before saving, or track created file paths and delete them if the batch fails.

### 17. Unhandled Parsing Error for Scam Report Dates
* **Location**: `routes/reports.py:59-60`
* **Problem**:
  Submitting an invalid date string format for `scam_date` raises a `ValueError` in `datetime.strptime()`, which is caught by the generic `except Exception` handler, resulting in a 500 Internal Server Error instead of a 400 Bad Request.
* **Recommended Fix**:
  Add explicit validation for `scam_date_str` and return an appropriate 400 error message if parsing fails.

### 18. SQLite Foreign Key Cascades Disabled by Default
* **Location**: `models/product_db.py:283-370`
* **Problem**:
  While `ondelete="CASCADE"` is defined on secondary product tables (`product_identifiers`, `product_images`, etc.), SQLite does not enforce foreign keys unless `PRAGMA foreign_keys = ON;` is explicitly executed on connection start. Additionally, SQLAlchemy `cascade="all, delete-orphan"` is omitted on `Product` relationships for these secondary tables, leading to orphaned rows in SQLite environments.
* **Recommended Fix**:
  Add `cascade="all, delete-orphan"` to the corresponding relationships in `Product`.

