# TrustLens Codebase Audit & Architecture Roadmap

---

## 1. Objective TrustScore & Health Index

### Overall Score: 52 / 100
*Status: Fragile / Production-Blocked (Needs Critical Remediation)*

The TrustScore reflects an objective, unvarnished evaluation of the TrustLens repository based on live static inspection, dependency verification, and runtime execution tracing. While the repository exhibits good functional compartmentalization into Flask Blueprints and rich domain-specific heuristic engines, multiple critical architectural defects—including a destructive database schema drop on boot, inverted risk scores, unmitigated SSRF, lack of CSRF, and worker thread starvation—preclude safe production deployment.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        TRUSTSCORE BREAKDOWN                            │
├───────────────────────────────────┬───────────────┬────────────────────┤
│ Dimension                         │ Score         │ Rating             │
├───────────────────────────────────┼───────────────┼────────────────────┤
│ 1. Architecture & Maintainability │ 18 / 25       │ Good               │
│ 2. Logic & Flow Integrity         │ 14 / 25       │ Needs Work         │
│ 3. Error Handling & Resilience    │ 12 / 25       │ High Risk          │
│ 4. Security & Data Safety         │ 08 / 25       │ Critical / Vulnerable │
├───────────────────────────────────┼───────────────┼────────────────────┤
│ FINAL COMPOSITE HEALTH INDEX      │ 52 / 100      │ HIGH RISK          │
└───────────────────────────────────┴───────────────┴────────────────────┘
```

---

### Pillar Breakdown

#### 1. Architecture & Maintainability: 18 / 25
* **Strengths**:
  * Clear application factory pattern in [`app_factory.py`](file:///Users/dineshchoudhary/Developer/kavita/trustlens-fresh/app_factory.py) keeping configuration, extensions, blueprints, and error handlers isolated.
  * Decoupled routing using modular Flask Blueprints ([`routes/auth.py`](file:///Users/dineshchoudhary/Developer/kavita/trustlens-fresh/routes/auth.py), [`routes/scanners.py`](file:///Users/dineshchoudhary/Developer/kavita/trustlens-fresh/routes/scanners.py), [`routes/admin.py`](file:///Users/dineshchoudhary/Developer/kavita/trustlens-fresh/routes/admin.py), [`routes/reports.py`](file:///Users/dineshchoudhary/Developer/kavita/trustlens-fresh/routes/reports.py)).
  * Relational normalization for the product/ingredient database in [`models/product_db.py`](file:///Users/dineshchoudhary/Developer/kavita/trustlens-fresh/models/product_db.py) separating core entities, variants, attributes, and safety classifications.
* **Deficits**:
  * Enormous monolithic service files: [`services/product_scanner.py`](file:///Users/dineshchoudhary/Developer/kavita/trustlens-fresh/services/product_scanner.py) exceeds 4,950 lines (~231 KB), [`services/website_scanner.py`](file:///Users/dineshchoudhary/Developer/kavita/trustlens-fresh/services/website_scanner.py) exceeds 1,570 lines, and [`services/email_scanner.py`](file:///Users/dineshchoudhary/Developer/kavita/trustlens-fresh/services/email_scanner.py) is over 1,340 lines.
  * In-memory linear iterations: functions like `_resolve_ingredient()` in [`routes/admin.py:291-300`](file:///Users/dineshchoudhary/Developer/kavita/trustlens-fresh/routes/admin.py#L291-L300) pull the entire `Ingredient` table into memory on every single ingredient lookup rather than utilizing SQL queries.
  * Missing schema migration harness (no Alembic / Flask-Migrate).

#### 2. Logic & Flow Integrity: 14 / 25
* **Strengths**:
  * Deterministic scoring pipeline in [`services/scoring.py`](file:///Users/dineshchoudhary/Developer/kavita/trustlens-fresh/services/scoring.py) utilizing the `ScoreBuilder` pattern with transparent reasons and severity classification.
  * Multi-stage image decoders in [`services/qr_scanner.py`](file:///Users/dineshchoudhary/Developer/kavita/trustlens-fresh/services/qr_scanner.py) attempting zxing-cpp, pyzbar, and OpenCV across contrast/scaling variants.
* **Deficits**:
  * **Inverted Score Definition**: In [`services/email_scanner.py:1287`](file:///Users/dineshchoudhary/Developer/kavita/trustlens-fresh/services/email_scanner.py#L1287), `score` is calculated as a *Risk Score* (0=safe, 100=danger) while all other scanners treat `score` as a *Trust Score* (100=safe, 0=danger). This inverts persisted scores in `EmailScan.trust_score` and pollutes AI monitoring logs.
  * **Worker Thread Lockup**: In [`services/whatsapp_scanner.py:86-89`](file:///Users/dineshchoudhary/Developer/kavita/trustlens-fresh/services/whatsapp_scanner.py#L86-L89), using `ThreadPoolExecutor` within a `with` context manager forces `pool.shutdown(wait=True)` upon exit, causing the thread to block indefinitely even after `TimeoutError` is triggered.
  * **Misleading False Positives**: In [`services/qr_scanner.py:603-612`](file:///Users/dineshchoudhary/Developer/kavita/trustlens-fresh/services/qr_scanner.py#L603-L612), an unreadable image or photo lacking a QR code is hard-assigned `status = "dangerous"` with `score = 0`, corrupting global risk statistics.

#### 3. Error Handling & Resilience: 12 / 25
* **Strengths**:
  * Defensive network lookups in threat intelligence services returning `None` or "unknown" rather than failing the scan.
  * Centralized logging wrapper in [`services/logger.py`](file:///Users/dineshchoudhary/Developer/kavita/trustlens-fresh/services/logger.py) with best-effort persistence.
* **Deficits**:
  * **Destructive Table Dropping on Boot**: In [`database/init_db.py:95`](file:///Users/dineshchoudhary/Developer/kavita/trustlens-fresh/database/init_db.py#L95), schema drift detection drops and recreates tables automatically upon detecting removed or retyped columns.
  * **Missing Database Rollbacks**: Admin mutation routes in [`routes/admin.py`](file:///Users/dineshchoudhary/Developer/kavita/trustlens-fresh/routes/admin.py) commit without `try...except` and `db.session.rollback()` wrappers, poisoning the SQLAlchemy session on database constraint violations.
  * **Fragile Connection String Parsing**: In [`database/init_db.py:50-55`](file:///Users/dineshchoudhary/Developer/kavita/trustlens-fresh/database/init_db.py#L50-L55), manual `.split()` slicing of MySQL URIs crashes if passwords contain `@` or `:` or if connection arguments exist.

#### 4. Security & Data Safety: 08 / 25
* **Strengths**:
  * Password hashing using Werkzeug's `generate_password_hash` and `check_password_hash`.
  * Secure session cookies configured with `SESSION_COOKIE_HTTPONLY=True` and `SESSION_COOKIE_SAMESITE="Lax"`.
* **Deficits**:
  * **Zero CSRF Protection**: `Flask-WTF` is not installed; no forms or API endpoints validate CSRF tokens, allowing cross-site request execution against authenticated users and admins.
  * **State Mutation via GET**: Endpoints like [`/admin/blacklist/<id>/delete`](file:///Users/dineshchoudhary/Developer/kavita/trustlens-fresh/routes/admin.py#L182) and [`/admin/messages/<id>/read`](file:///Users/dineshchoudhary/Developer/kavita/trustlens-fresh/routes/admin.py#L251) execute database deletions and updates over unauthenticated/unprotected HTTP GET requests.
  * **Server-Side Request Forgery (SSRF)**: [`services/website_scanner.py:237`](file:///Users/dineshchoudhary/Developer/kavita/trustlens-fresh/services/website_scanner.py#L237) and [`services/job_scanner.py:214`](file:///Users/dineshchoudhary/Developer/kavita/trustlens-fresh/services/job_scanner.py#L214) connect to arbitrary user-supplied URLs without private/loopback/metadata IP blocking.
  * **Open Redirect**: In [`routes/auth.py:31-33`](file:///Users/dineshchoudhary/Developer/kavita/trustlens-fresh/routes/auth.py#L31-L33), unvalidated `next` parameter redirects users to external phishing domains.
  * **Unverified File Uploads**: In [`routes/reports.py:47-56`](file:///Users/dineshchoudhary/Developer/kavita/trustlens-fresh/routes/reports.py#L47-L56), uploaded files are checked only by extension without verifying image headers or size limits.

---

### Strengths & Reliable Patterns (What is Working Well)
1. **Sophisticated Domain Verification Heuristics**:
   The verification engines are not toy implementations. `website_scanner.py` features genuine TLS certificate inspection, public suffix normalization via `MULTI_LABEL_TLDS`, Cyrillic/Greek homograph detection via character mapping, and preloaded HSTS checks.
2. **Comprehensive Forensics in Payment Verification**:
   [`services/payment_forensics.py`](file:///Users/dineshchoudhary/Developer/kavita/trustlens-fresh/services/payment_forensics.py) executes genuine Error Level Analysis (ELA) and copy-move block matching using OpenCV and NumPy, effectively identifying cloned text and compression artifacts.
3. **Thorough Normalization of Product Knowledge Base**:
   [`models/product_db.py`](file:///Users/dineshchoudhary/Developer/kavita/trustlens-fresh/models/product_db.py) defines a clean, relational hierarchy: `Product` -> `ProductIngredient` -> `Ingredient`, supporting multiple identifiers (GTIN, SKU, barcodes) and category trees.
4. **Defensive External Integrations**:
   Threat APIs (Google Safe Browsing, VirusTotal, RDAP) are treated strictly as additive evidence; timeouts or missing API keys fail open to "unknown" rather than crashing requests or penalizing users.

---

### Weaknesses & Structural Risks (What is Failing or Risky)
1. **Data Loss by Design**:
   The schema auto-healing in `database/init_db.py` will purge entire tables if a developer renames a column in a model, wiping production scan histories and user reports on reboot.
2. **Inverted Mental Model for Email Scanning**:
   A 95% risk email (phishing) is saved with `trust_score=95`, and a 5% risk email (safe) is saved with `trust_score=5`. The user dashboard, database queries, and AI logs interpret high scores as safe, completely breaking data integrity for emails.
3. **Severe SSRF & Intranet Exposure**:
   Any user can submit `http://127.0.0.1:5000`, `http://169.254.169.254/latest/meta-data/`, or internal Redis/MySQL ports, turning the server into a port-scanning proxy.
4. **Denial of Service via Heavy Synchronous Processing**:
   Running OCR (`EasyOCR`), image manipulation, and 14-day timeseries aggregations synchronously inside Flask HTTP request workers will rapidly exhaust Gunicorn/uWSGI worker pools under minimal concurrency.

---

## 2. Comprehensive Logic, Bug, & Flow Audit

### Critical Priority Issues

#### Issue 1: Destructive Auto-Drop of Live Database Tables on Schema Drift
* **Location**: [`database/init_db.py:84-95`](file:///Users/dineshchoudhary/Developer/kavita/trustlens-fresh/database/init_db.py#L84-L95)
* **Issue & Flow Break**:
  `_verify_schema()` checks live columns against SQLAlchemy model definitions on every application boot. If any column is removed from a model (or renamed, or if manual columns exist in the DB), `added and not removed` evaluates to `False`. The `else` branch executes:
  ```python
  _drop_table(app, table.name)
  ```
  This immediately drops the table using `DROP TABLE IF EXISTS` (disabling foreign key checks in MySQL). In a deployment where models are refactored, all customer accounts, verified products, scam reports, and scan histories are wiped on restart.
* **Concrete Fix**:
  Delete the destructive `_drop_table` call entirely. Schema drift should only be handled via formal migration scripts (e.g. Alembic) or non-destructive warnings.
  ```diff
  --- a/database/init_db.py
  +++ b/database/init_db.py
  @@ -92,4 +92,4 @@ def _verify_schema(app) -> None:
               if added and not removed:
                   _add_missing_columns(app, table, added)
  -            else:
  -                _drop_table(app, table.name)
  +            elif removed:
  +                app.logger.warning("Table '%s' has removed columns: %s. Manual migration required.", table.name, removed)
  ```

---

#### Issue 2: Inverted Score Semantics in Email Scanner Breaking Persistence & Analytics
* **Location**: [`services/email_scanner.py:1287-1337`](file:///Users/dineshchoudhary/Developer/kavita/trustlens-fresh/services/email_scanner.py#L1287-L1337)
* **Issue & Flow Break**:
  Across the system, `trust_score` represents trust (100 = safe, 0 = dangerous). In `services/email_scanner.py`, `risk` is calculated as 0–100 risk (0 = very low risk, 100 = very high risk). Line 1287 outputs `"score": risk`. 
  When `persist_scan()` is called (line 1336):
  ```python
  scan = EmailScan(..., trust_score=payload["score"], status=payload["status"])
  ```
  A safe email with 5% risk is stored with `trust_score = 5`. A dangerous phishing email with 95% risk is stored with `trust_score = 95`. This inverts sorting, dashboard charts, and platform-wide security reports.
* **Concrete Fix**:
  Derive `trust_score = 100 - risk` and output both `score` (trust) and `risk_score` (risk):
  ```diff
  --- a/services/email_scanner.py
  +++ b/services/email_scanner.py
  @@ -1284,7 +1284,8 @@ def scan_email(content: str, trace: bool = False) -> dict:
       processing_ms = int((time.perf_counter() - start) * 1000)
  +    trust_score = max(0, min(100, 100 - risk))
   
       result = {
  -        "score": risk,
  +        "score": trust_score,
  +        "risk_score": risk,
           "status": cat["status"],
  ```

---

#### Issue 3: Server-Side Request Forgery (SSRF) and Unbounded Ingestion in Scanners
* **Location**: [`services/website_scanner.py:237`](file:///Users/dineshchoudhary/Developer/kavita/trustlens-fresh/services/website_scanner.py#L237), [`services/website_scanner.py:329-331`](file:///Users/dineshchoudhary/Developer/kavita/trustlens-fresh/services/website_scanner.py#L329-L331), [`services/job_scanner.py:214-219`](file:///Users/dineshchoudhary/Developer/kavita/trustlens-fresh/services/job_scanner.py#L214-L219)
* **Issue & Flow Break**:
  Both scanners accept raw URLs from users and make socket/HTTP requests without validating resolved IP addresses. An attacker can submit:
  * `http://127.0.0.1:5000` or `http://localhost:3306` (intranet port scanning)
  * `http://169.254.169.254/latest/meta-data/` (cloud IAM credential extraction)
  * `allow_redirects=True` allows bypass via open redirectors.
  * In `_fetch_page()`, reading `resp.content` without byte streaming allows an attacker to return a 5 GB response, causing memory exhaustion (OOM crash).
* **Concrete Fix**:
  Add an IP validation utility that resolves the target host and rejects non-public IP addresses prior to connecting, and stream HTTP downloads with a hard byte cap:
  ```python
  # services/network_security.py
  import socket, ipaddress

  def validate_public_host(host: str) -> bool:
      try:
          ip_str = socket.gethostbyname(host)
          ip = ipaddress.ip_address(ip_str)
          return not (ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved)
      except Exception:
          return False
  ```
  ```diff
  --- a/services/website_scanner.py
  +++ b/services/website_scanner.py
  @@ -328,4 +328,7 @@ def _fetch_page(url: str, timeout: int) -> dict:
  +        host = _host_port(_netloc(url))[0]
  +        if not validate_public_host(host):
  +            return None, "Blocked: Target resolves to a private or restricted address."
           resp = session.get(
               url, timeout=timeout, allow_redirects=False, verify=verify, stream=True
           )
  ```

---

#### Issue 4: Zero CSRF Protection & State Mutation on GET Handlers
* **Location**: [`app_factory.py:17-67`](file:///Users/dineshchoudhary/Developer/kavita/trustlens-fresh/app_factory.py#L17-L67), [`routes/admin.py:182-190`](file:///Users/dineshchoudhary/Developer/kavita/trustlens-fresh/routes/admin.py#L182-L190), [`routes/admin.py:251-258`](file:///Users/dineshchoudhary/Developer/kavita/trustlens-fresh/routes/admin.py#L251-L258)
* **Issue & Flow Break**:
  `Flask-WTF` is missing from `requirements.txt`. No forms or AJAX endpoints include CSRF tokens. Worse, the following destructive operations are exposed on HTTP GET:
  * `GET /admin/blacklist/<domain_id>/delete` -> removes a blacklisted domain.
  * `GET /admin/messages/<msg_id>/read` -> mutates message read status.
  If an authenticated admin views a third-party website with an embedded `<img src="http://localhost:5000/admin/blacklist/1/delete">`, the browser will transmit session cookies and execute the deletion automatically.
* **Concrete Fix**:
  1. Add `Flask-WTF>=1.2.1` to `requirements.txt` and initialize `CSRFProtect(app)` in `app_factory.py`.
  2. Change GET endpoints to POST:
  ```diff
  --- a/routes/admin.py
  +++ b/routes/admin.py
  @@ -182,3 +182,3 @@ def blacklist_add():
  -@admin_bp.route("/blacklist/<int:domain_id>/delete")
  +@admin_bp.route("/blacklist/<int:domain_id>/delete", methods=["POST"])
   @admin_required
   def blacklist_delete(domain_id):
  ```

---

#### Issue 5: Open Redirect Vulnerability in Authentication Flow
* **Location**: [`routes/auth.py:31-33`](file:///Users/dineshchoudhary/Developer/kavita/trustlens-fresh/routes/auth.py#L31-L33)
* **Issue & Flow Break**:
  ```python
  next_page = request.args.get("next")
  return redirect(next_page or url_for("dashboard.index"))
  ```
  `next_page` is not validated. An attacker can construct:
  `https://trustlens.io/auth/login?next=https://attacker-phishing.com` or `//attacker-phishing.com`
  After successful credentials entry, the user is redirected off-site to the phishing host.
* **Concrete Fix**:
  Validate `next_page` using `urllib.parse.urlsplit` to ensure it is relative and does not begin with `//`:
  ```diff
  --- a/routes/auth.py
  +++ b/routes/auth.py
  @@ -6,2 +6,3 @@ import re
  +from urllib.parse import urlsplit
  @@ -31,3 +32,5 @@ def login():
               next_page = request.args.get("next")
  +            if next_page and (urlsplit(next_page).netloc != "" or next_page.startswith("//")):
  +                next_page = None
               flash(f"Welcome back, {user.full_name}!", "success")
  ```

---

#### Issue 6: EasyOCR ThreadPoolExecutor Timeout Lockup (Worker Hang)
* **Location**: [`services/whatsapp_scanner.py:86-89`](file:///Users/dineshchoudhary/Developer/kavita/trustlens-fresh/services/whatsapp_scanner.py#L86-L89)
* **Issue & Flow Break**:
  ```python
  with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
      future = pool.submit(reader.readtext, image_path, detail=0, paragraph=True)
      lines = future.result(timeout=Config.OCR_TIMEOUT_SECONDS)
  ```
  In Python, exiting a `with ThreadPoolExecutor(...)` block invokes `pool.shutdown(wait=True)`. When `future.result()` raises a `TimeoutError`, the context manager catches the unwind but blocks on `pool.shutdown(wait=True)` until `reader.readtext()` completes. The timeout does not protect the thread, leading to thread exhaustion under concurrent OCR requests.
* **Concrete Fix**:
  Instantiate the pool without the context manager and explicitly invoke `pool.shutdown(wait=False, cancel_futures=True)` on timeout:
  ```diff
  --- a/services/whatsapp_scanner.py
  +++ b/services/whatsapp_scanner.py
  @@ -85,5 +85,9 @@ def extract_text_ocr(image_path: str) -> str:
       try:
           reader = _get_reader()
  -        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
  -            future = pool.submit(reader.readtext, image_path, detail=0, paragraph=True)
  -            lines = future.result(timeout=Config.OCR_TIMEOUT_SECONDS)
  +        pool = concurrent.futures.ThreadPoolExecutor(max_workers=1)
  +        try:
  +            future = pool.submit(reader.readtext, image_path, detail=0, paragraph=True)
  +            lines = future.result(timeout=Config.OCR_TIMEOUT_SECONDS)
  +            pool.shutdown(wait=False)
  +        except concurrent.futures.TimeoutError:
  +            pool.shutdown(wait=False, cancel_futures=True)
  +            raise
  ```

---

### Medium Priority Issues

#### Issue 7: Unverified File Uploads and MIME-Type Spoofing in Scam Reports
* **Location**: [`routes/reports.py:47-56`](file:///Users/dineshchoudhary/Developer/kavita/trustlens-fresh/routes/reports.py#L47-L56)
* **Issue & Flow Break**:
  `submit_report()` verifies uploads using only the file extension (`ext in ALLOWED_IMAGE_EXTENSIONS`). Unlike `routes/scanners.py`, it does not invoke `_verify_image_file()`. An attacker can upload arbitrary non-image files (HTML containing `<script>`, SVG polyglots, or oversized binaries) with a `.png` extension, which are saved directly into `static/uploads/screenshots/` and served with user-controlled content types.
* **Concrete Fix**:
  Verify the image with Pillow `Image.open().verify()` and check file size caps before saving:
  ```python
  from PIL import Image
  with Image.open(file.stream) as img:
      img.verify()
  file.stream.seek(0)
  ```

---

#### Issue 8: Missing Transaction Rollbacks on Admin Database Mutations
* **Location**: [`routes/admin.py:439-452`](file:///Users/dineshchoudhary/Developer/kavita/trustlens-fresh/routes/admin.py#L439-L452), [`routes/admin.py:486-500`](file:///Users/dineshchoudhary/Developer/kavita/trustlens-fresh/routes/admin.py#L486-L500), [`routes/admin.py:599-603`](file:///Users/dineshchoudhary/Developer/kavita/trustlens-fresh/routes/admin.py#L599-L603), [`routes/admin.py:656-659`](file:///Users/dineshchoudhary/Developer/kavita/trustlens-fresh/routes/admin.py#L656-L659)
* **Issue & Flow Break**:
  In `product_new`, `product_edit`, `ingredient_add`, and `category_add`, `db.session.commit()` is executed without a `try...except ... db.session.rollback()` structure. If an `IntegrityError` occurs (e.g. duplicate category or duplicate product-ingredient pairing), an unhandled 500 error is thrown and the SQLAlchemy session remains in a dirty/failed state for that worker process.
* **Concrete Fix**:
  Wrap all administrative mutations in `try...except` blocks that roll back the session and display user-friendly flash messages.

---

#### Issue 9: Race Condition in Product ID Generation
* **Location**: [`routes/admin.py:388-396`](file:///Users/dineshchoudhary/Developer/kavita/trustlens-fresh/routes/admin.py#L388-L396)
* **Issue & Flow Break**:
  ```python
  def _generate_product_id(brand_name: str, product_name: str) -> str:
      base = "PRD-" + _norm(f"{brand_name} {product_name}").upper()[:36]
      candidate = base
      n = 1
      while db.session.get(Product, candidate):
          candidate = f"{base}-{n}"
          n += 1
      return candidate
  ```
  This non-atomic check-then-insert allows two concurrent requests adding the same product to generate identical IDs, resulting in an unhandled database `IntegrityError`.
* **Concrete Fix**:
  Append a short random UUID token (e.g., `uuid.uuid4().hex[:6]`) to guarantee uniqueness.

---

#### Issue 10: Massive N+1 Query Multiplication in Analytics and Admin Views
* **Location**: [`services/analytics.py:82-98`](file:///Users/dineshchoudhary/Developer/kavita/trustlens-fresh/services/analytics.py#L82-L98), [`routes/admin.py:291-300`](file:///Users/dineshchoudhary/Developer/kavita/trustlens-fresh/routes/admin.py#L291-L300), [`routes/dashboard.py:24-37`](file:///Users/dineshchoudhary/Developer/kavita/trustlens-fresh/routes/dashboard.py#L24-L37)
* **Issue & Flow Break**:
  * `scan_volume_timeseries()` executes `8 models * 14 days = 112` separate `COUNT()` SQL queries synchronously per request.
  * `_resolve_ingredient()` calls `Ingredient.query.all()` on every line of an ingredient submission, fetching all ingredient rows into Python memory for client-side matching.
  * `_counts()` runs 18 individual SQL count queries on every dashboard load.
* **Concrete Fix**:
  Use SQL `GROUP BY` and date-truncation queries, and search ingredients using database indices:
  ```python
  # Replace 112 queries with a single aggregation query per model:
  db.session.query(
      db.func.date(m.created_at), db.func.count(m.id)
  ).filter(m.created_at >= start).group_by(db.func.date(m.created_at)).all()
  ```

---

#### Issue 11: Database Mutation on GET Request in Dashboard Route
* **Location**: [`routes/dashboard.py:64-71`](file:///Users/dineshchoudhary/Developer/kavita/trustlens-fresh/routes/dashboard.py#L64-L71)
* **Issue & Flow Break**:
  ```python
  for report in my_reports:
      for reply in report.replies:
          if not reply.is_viewed:
              reply.is_viewed = True
  db.session.commit()
  ```
  HTTP GET must remain idempotent. Search engine pre-fetching, link unfurlers, or browser reloads automatically clear unread reply notifications without user engagement.
* **Concrete Fix**:
  Clear notification status via an explicit POST request (e.g. `POST /api/reports/<id>/mark-viewed`) triggered when the user opens the report.

---

#### Issue 12: Non-QR Images Misclassified as Malicious
* **Location**: [`services/qr_scanner.py:603-612`](file:///Users/dineshchoudhary/Developer/kavita/trustlens-fresh/services/qr_scanner.py#L603-L612)
* **Issue & Flow Break**:
  When an uploaded image does not contain a QR code, `scan_qr_image()` returns:
  ```python
  return {"score": 0, "status": "dangerous", "verdict": "No QR Code Detected", ...}
  ```
  This is committed to the database as a "dangerous" scan, polluting the user's history and falsely inflating platform risk statistics.
* **Concrete Fix**:
  Return an unprocessable result (`status = "unverifiable"` or HTTP 422) instead of classifying non-QR images as high-risk malicious attacks.

---

#### Issue 13: Fragile MySQL URI String Parsing
* **Location**: [`database/init_db.py:50-55`](file:///Users/dineshchoudhary/Developer/kavita/trustlens-fresh/database/init_db.py#L50-L55)
* **Issue & Flow Break**:
  ```python
  host_part = uri.split("@")[1].split("/")[0]
  user = uri.split("//")[1].split(":")[0]
  password = uri.split("//")[1].split(":")[1].split("@")[0]
  ```
  If a MySQL password contains `@` or `:`, or if URL query parameters (e.g. `?charset=utf8mb4`) are present, parsing fails with `IndexError` or connects with corrupt credentials.
* **Concrete Fix**:
  Use `urllib.parse.urlsplit` or `sqlalchemy.engine.make_url(uri)`.

---

#### Issue 14: User Dashboard Omits 7 Out of 8 Scan Types
* **Location**: [`routes/dashboard.py:44-46`](file:///Users/dineshchoudhary/Developer/kavita/trustlens-fresh/routes/dashboard.py#L44-L46), [`templates/dashboard.html:39-70`](file:///Users/dineshchoudhary/Developer/kavita/trustlens-fresh/templates/dashboard.html#L39-L70)
* **Issue & Flow Break**:
  The dashboard displays summary counters for all 8 scan models, but the "Recent Scans" table queries only `WebsiteScan`. Scans performed via Email, QR, Payment, Job, Product, WhatsApp, or Claim checkers never appear on the user dashboard.
* **Concrete Fix**:
  Implement a polymorphic or unified recent scans view across models.

---

### Low Priority Issues & Code Smells

#### Issue 15: Deprecated `datetime.utcnow` Across All Models
* **Location**: `models/user.py:24`, `models/scan.py:16`, `models/report.py:43`, `models/product_db.py:53`, `models/product_candidate.py:48`, `models/admin.py:19`
* **Issue**: `datetime.utcnow` is deprecated in Python 3.12 and scheduled for removal.
* **Fix**: Use `lambda: datetime.now(timezone.utc)`.

#### Issue 16: Orphaned Files on Multi-Image Upload Failure
* **Location**: [`routes/scanners.py:316-324`](file:///Users/dineshchoudhary/Developer/kavita/trustlens-fresh/routes/scanners.py#L316-L324)
* **Issue**: Uploaded product images are saved to disk sequentially before validation. If image 2 fails verification, image 1 is left orphaned on disk permanently.
* **Fix**: Validate image streams in memory prior to saving, or delete written files in cleanup handlers.

#### Issue 17: Unhandled ValueError on Scam Report Date Format
* **Location**: [`routes/reports.py:59-60`](file:///Users/dineshchoudhary/Developer/kavita/trustlens-fresh/routes/reports.py#L59-L60)
* **Issue**: Malformed `scam_date` strings trigger an unhandled `ValueError` inside `strptime`, resulting in a 500 server error instead of a 400 validation error.
* **Fix**: Wrap `strptime` in a `try...except ValueError` block and return an informative 400 error.

#### Issue 18: SQLite Foreign Key Cascades Disabled by Default
* **Location**: [`models/product_db.py:283-370`](file:///Users/dineshchoudhary/Developer/kavita/trustlens-fresh/models/product_db.py#L283-L370)
* **Issue**: Secondary product tables (`product_identifiers`, `product_images`, etc.) omit SQLAlchemy-level `cascade="all, delete-orphan"`. In SQLite, `PRAGMA foreign_keys = ON;` is disabled by default, leaving orphaned records when products are deleted.
* **Fix**: Add `cascade="all, delete-orphan"` to `Product` model relationships.

---

## 3. Database Scaling & Migration Blueprint

### Current Storage Identification
TrustLens currently uses **Flask-SQLAlchemy 3.x** backed by either:
1. **SQLite (`database/trustlens.db`)**: Default mode for local development.
2. **MySQL (`mysql+pymysql`)**: Enabled via `USE_MYSQL=1` or `DATABASE_URL`.

Schema management relies on custom Python reflection in [`database/init_db.py`](file:///Users/dineshchoudhary/Developer/kavita/trustlens-fresh/database/init_db.py) and a ~2,000-line declarative seeding script in [`database/seed_product_db.py`](file:///Users/dineshchoudhary/Developer/kavita/trustlens-fresh/database/seed_product_db.py). Uploaded media (screenshots, QR images, product labels) is saved to the local filesystem under `static/uploads/`.

---

### Scaling Bottlenecks
1. **Concurrency Lock Contention in SQLite**:
   SQLite locks the entire database file during writes. Under concurrent scanning and reporting traffic, requests encounter `sqlite3.OperationalError: database is locked`.
2. **Schema Drift Catastrophe (Auto-Drop)**:
   The lack of a formal migration tool (like Alembic) combined with the boot-time column reconciliation script risks catastrophic data loss on restart.
3. **Heavy N+1 Query Aggregations**:
   The admin analytics dashboard runs hundreds of synchronized count queries across 8 independent scan tables. As table row counts reach tens of thousands, dashboard response times will degrade significantly.
4. **Local Disk Exhaustion**:
   Storing media in `static/uploads/` prevents horizontal scaling across multiple application instances, as uploaded files are not shared across server nodes.

---

### Recommended Database Architecture

#### Target Engine: PostgreSQL 16+
PostgreSQL is the optimal database engine for TrustLens due to:
* Native JSONB support with GIN indexing for flexible scanner payloads (`reasons`, `flags`, `metadata`).
* Robust full-text search and trigram matching (`pg_trgm`) for fuzzy product and ingredient lookups.
* High-concurrency Row-Level Locking (MVCC).
* Compatibility with managed cloud engines (AWS Aurora, Google Cloud SQL, Supabase, Neon).

```
┌─────────────────────────────────────────────────────────────┐
│                    HIGH-SCALE ARCHITECTURE                   │
└─────────────────────────────────────────────────────────────┘
                               │
                       [ Load Balancer ]
                               │
                 ┌─────────────┴─────────────┐
                 ▼                           ▼
        [ Web / API Worker 1 ]      [ Web / API Worker 2 ]
                 │                           │
                 ├───────────────────────────┤
                 ▼                           ▼
          [ Redis Cluster ]           [ S3 / Cloud Storage ]
          - Session cache             - User screenshots
          - Celery task queue         - QR images
          - Query result cache        - Product labels
                 │
                 ▼
          [ PgBouncer Pool ]
                 │
                 ▼
        [ PostgreSQL 16+ Primary ] ◄── [ Read Replica ]
        - Core relational schema
        - Partitioned scan logs
        - GIN / Trigram indices
```

---

### Target Schema Optimization

#### 1. Unified Partitioned Scan Model
Consolidate the 8 fragmented scan tables into a partitioned `scans` table to allow single-query analytics across all scanner types:

```sql
CREATE TABLE scans (
    id BIGSERIAL,
    user_id INT REFERENCES users(id) ON DELETE SET NULL,
    scan_type VARCHAR(32) NOT NULL, -- 'website', 'email', 'qr', 'payment', 'job', 'product', 'claim', 'whatsapp'
    trust_score SMALLINT NOT NULL CHECK (trust_score BETWEEN 0 AND 100),
    status VARCHAR(16) NOT NULL,    -- 'safe', 'warning', 'dangerous', 'unverifiable'
    target_identifier VARCHAR(512), -- URL, email sender, product name, etc.
    reasons JSONB NOT NULL DEFAULT '[]'::jsonb,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

-- Create monthly partitions
CREATE TABLE scans_2026_09 PARTITION OF scans
    FOR VALUES FROM ('2026-09-01') TO ('2026-10-01');
CREATE TABLE scans_2026_10 PARTITION OF scans
    FOR VALUES FROM ('2026-10-01') TO ('2026-11-01');

-- Indices for rapid lookup & analytics
CREATE INDEX idx_scans_created_at ON scans (created_at DESC);
CREATE INDEX idx_scans_type_status ON scans (scan_type, status);
CREATE INDEX idx_scans_reasons_gin ON scans USING GIN (reasons);
```

#### 2. Fuzzy Text Search on Products and Ingredients
Replace Python in-memory scans with PostgreSQL trigram indexing:

```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE INDEX idx_ingredients_name_trgm ON ingredients USING GIN (ingredient_name gin_trgm_ops);
CREATE INDEX idx_ingredients_norm_trgm ON ingredients USING GIN (normalized_name gin_trgm_ops);
CREATE INDEX idx_products_search ON products USING GIN ((brand_name || ' ' || product_name) gin_trgm_ops);
```

---

### Connection Pooling & Caching Strategy
1. **Connection Pooling with PgBouncer**:
   * Deploy PgBouncer in front of PostgreSQL using transaction pooling (`pool_mode = transaction`).
   * Cap PostgreSQL direct connections to `max_connections = 100` while allowing hundreds of web worker threads to multiplex connections cleanly.
2. **Redis Caching Tier**:
   * **Dashboard Counts**: Cache platform-wide statistics in Redis (`SET platform:counts ... EX 60`). Invalidate via Celery background tasks or write-through updates.
   * **Ingredient Lookup Cache**: Store compiled ingredient dictionaries in Redis hashes (`HSET ingredient:cache ...`) to eliminate repetitive database queries during bulk label analysis.
   * **Async Background Queue (Celery / Redis Queue)**:
     Offload OCR extraction (`EasyOCR`) and outbound HTTP checks (`requests.get`) to background Celery workers. The HTTP request immediately receives a job ID and polls or streams results via WebSockets/SSE, preventing web worker starvation.

---

### Step-by-Step Zero-Downtime Migration Plan

```
┌────────────────────────────────────────────────────────────────────────┐
│                        4-PHASE MIGRATION PLAN                          │
├────────────────────────────────────────────────────────────────────────┤
│ Phase 1: Database Provisioning & Alembic Setup                         │
│ Phase 2: Dual-Writing & Historical Data Migration                      │
│ Phase 3: Traffic Switch & Verification                                 │
│ Phase 4: S3 Media Decoupling & Legacy Cleanup                          │
└────────────────────────────────────────────────────────────────────────┘
```

#### Phase 1: Provisioning & Migration Baseline
1. Provision a PostgreSQL 16+ instance (e.g., Supabase / AWS RDS).
2. Install `Flask-Migrate` (`alembic`) and `psycopg2-binary`:
   ```bash
   pip install Flask-Migrate psycopg2-binary
   flask db init
   flask db migrate -m "Baseline TrustLens schema"
   ```
3. Apply the migration baseline to the target PostgreSQL database:
   ```bash
   DATABASE_URL="postgresql://user:pass@host:5432/trustlens" flask db upgrade
   ```

#### Phase 2: Historical Data Dump & Import
1. Export existing data from SQLite / MySQL into PostgreSQL-compatible CSV or JSON dumps using a data pipeline script:
   ```bash
   python -m scripts.migrate_data --source sqlite:///database/trustlens.db --target postgresql://...
   ```
2. Reset PostgreSQL sequences to match imported primary keys:
   ```sql
   SELECT setval('users_id_seq', (SELECT MAX(id) FROM users));
   SELECT setval('scam_reports_id_seq', (SELECT MAX(id) FROM scam_reports));
   ```

#### Phase 3: Traffic Cutover & Zero-Downtime Switch
1. Update `.env` or application config in production to point `DATABASE_URL` to PgBouncer / PostgreSQL.
2. Disable the legacy `_verify_schema()` and `_drop_table()` routines in `init_db.py`.
3. Restart application workers with zero downtime using Gunicorn rolling restarts (`kill -HUP <master_pid>`).
4. Validate API health, login flows, and scanner persistence against the PostgreSQL backend.

#### Phase 4: Object Storage (S3) Decoupling
1. Update `_save_upload()` in `routes/scanners.py` and `routes/reports.py` to stream files directly to an S3-compatible bucket (AWS S3, Cloudflare R2, or MinIO) using `boto3`.
2. Migrate existing assets in `static/uploads/` to the cloud bucket using `aws s3 sync static/uploads/ s3://trustlens-media/uploads/`.
3. Serve media assets through a secure CDN distribution.

