# TrustLens Codebase Remediation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Resolve all 18 identified critical, medium, and low security, data safety, logic, and performance defects across the TrustLens codebase without breaking existing verification functionality.

**Architecture:** Introduce a dedicated network security validation module to block SSRF and payload bombs; install CSRF protection and eliminate state-modifying GET handlers; remove destructive auto-drop logic from database bootstrap; normalize email scoring to standard 0–100 Trust Score semantics; unblock thread pool timeouts in EasyOCR; and optimize database queries using SQL aggregations and indexed lookups.

**Tech Stack:** Python 3.10+, Flask 3.x, Flask-SQLAlchemy 3.x, Flask-WTF, Flask-Login, Werkzeug, Pillow, OpenCV, EasyOCR, SQLite/MySQL.

**Spec:** [`docs/superpowers/specs/2026-09-24-codebase-remediation-design.md`](file:///Users/dineshchoudhary/Developer/kavita/trustlens-fresh/docs/superpowers/specs/2026-09-24-codebase-remediation-design.md)

---

## Global Constraints

- Never drop live database tables during runtime initialization or schema verification.
- Trust scores across all scanners must strictly adhere to the `0..100` scale where `100` is Safe and `0` is Dangerous (`status = classify(score)`).
- Never allow outbound HTTP or socket connections to private, loopback, or cloud-metadata IP ranges.
- State-changing actions must never be triggered via HTTP GET requests.
- All database write operations must be wrapped in `try...except` blocks that execute `db.session.rollback()` on failure.
- Preserve backward-compatible JSON response envelopes: `{"success": bool, "error": str|None, ...}`.

---

## Review Focus

1. **Private Network Bypass via DNS Rebinding or Redirects**: Verify that resolved IP addresses are checked immediately prior to connecting and redirect destinations are validated.
2. **Open Redirect Protocol-Relative Attacks**: Verify that `//evil.com` or `https://evil.com` in `?next=` are rejected and default to `/dashboard`.
3. **CSRF Enforcement on Forms vs API Exemption**: Verify that web forms require CSRF tokens while internal scanner AJAX requests include the `X-CSRFToken` header.
4. **Email Scanner Score Inversion**: Verify that an email with 0% risk receives a trust score of 100 and safe status, not 0.
5. **EasyOCR Timeout Recovery**: Verify that when `extract_text_ocr` times out, the worker thread is terminated without freezing Flask.

---

## Tasks

### Task 1: Network Security Module (SSRF Guard & Stream Limits)

**Files:**
- Create: `services/network_security.py`
- Modify: `services/website_scanner.py:227-360`
- Modify: `services/job_scanner.py:210-233`
- Test: `tests/test_network_security.py`

**Interfaces:**
- Consumes: `urllib.parse.urlsplit`, `socket.getaddrinfo`, `ipaddress.ip_address`.
- Produces: `validate_public_url(url: str) -> tuple[bool, str]`.

- [ ] **Step 1: Write the failing test for SSRF validation**

Create `tests/test_network_security.py`:
```python
import pytest
from services.network_security import validate_public_url

def test_blocks_private_and_loopback_ips():
    assert validate_public_url("http://127.0.0.1:5000")[0] is False
    assert validate_public_url("http://localhost:8080")[0] is False
    assert validate_public_url("http://10.0.0.1")[0] is False
    assert validate_public_url("http://192.168.1.1")[0] is False
    assert validate_public_url("http://172.16.0.1")[0] is False
    assert validate_public_url("http://169.254.169.254/latest/meta-data/")[0] is False

def test_blocks_invalid_schemes():
    assert validate_public_url("file:///etc/passwd")[0] is False
    assert validate_public_url("ftp://example.com")[0] is False

def test_allows_public_domains():
    is_valid, _ = validate_public_url("https://google.com")
    assert is_valid is True
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests/test_network_security.py`  
Expected: `ModuleNotFoundError: No module named 'services.network_security'`

- [ ] **Step 3: Implement `services/network_security.py` and integrate guards**

Create `services/network_security.py`:
```python
"""
Network security helpers: SSRF defense and URL validation.
"""
import ipaddress
import socket
from urllib.parse import urlsplit


def validate_public_url(url: str) -> tuple[bool, str]:
    """
    Ensure a URL targets a public HTTP(S) address and does not resolve to private,
    loopback, link-local, or cloud-metadata IPs. Returns (is_valid, reason).
    """
    if not url:
        return False, "URL cannot be empty."

    parsed = urlsplit(url)
    if parsed.scheme.lower() not in ("http", "https"):
        return False, "Unsupported URL scheme (only HTTP and HTTPS are permitted)."

    host = parsed.hostname
    if not host:
        return False, "Invalid URL host."

    # Direct IP string check
    try:
        ip = ipaddress.ip_address(host)
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
            return False, f"Access to private/restricted IP ({host}) is blocked."
        return True, ""
    except ValueError:
        pass  # Host is a domain name

    # DNS resolution check
    try:
        addr_info = socket.getaddrinfo(host, parsed.port or (443 if parsed.scheme == "https" else 80))
        for item in addr_info:
            sockaddr = item[4]
            ip_str = sockaddr[0]
            ip = ipaddress.ip_address(ip_str)
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
                return False, f"Domain {host} resolves to private/restricted IP ({ip_str})."
    except socket.gaierror:
        return False, f"Could not resolve domain: {host}"
    except Exception as exc:
        return False, f"DNS validation error: {str(exc)}"

    return True, ""
```

In `services/website_scanner.py`:
Add guard in `_tls_probe` and `_fetch_page`. In `_fetch_page`, stream with maximum 2MB size cap:
```python
from services.network_security import validate_public_url

# In _tls_probe:
valid, err_msg = validate_public_url(f"https://{host}")
if not valid:
    return {"valid": False, "not_after": None, "issuer": "", "error": err_msg}

# In _fetch_page attempt():
valid, err_msg = validate_public_url(url)
if not valid:
    return None, f"blocked:{err_msg}"

resp = session.get(url, timeout=timeout, allow_redirects=False, verify=verify, stream=True)
# Read up to 2MB:
content_chunks = []
total_bytes = 0
for chunk in resp.iter_content(chunk_size=16384):
    content_chunks.append(chunk)
    total_bytes += len(chunk)
    if total_bytes > 2 * 1024 * 1024:
        break
resp._content = b"".join(content_chunks)
```

In `services/job_scanner.py`:
In `_probe(url: str)`:
```python
from services.network_security import validate_public_url

valid, _ = validate_public_url(url)
if not valid:
    return {"ok": False, "parked": False, "blocked": True, "url": None}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest tests/test_network_security.py`  
Expected: All tests pass.

- [ ] **Step 5: Commit**

```bash
git add services/network_security.py services/website_scanner.py services/job_scanner.py tests/test_network_security.py
git commit -m "security: add SSRF protection and response size caps to scanners"
```

---

### Task 2: Open Redirect & File Upload Hardening

**Files:**
- Modify: `routes/auth.py:20-37`
- Modify: `routes/reports.py:47-61`
- Test: `tests/test_auth_and_reports_security.py`

**Interfaces:**
- Consumes: `urllib.parse.urlsplit`, `routes.scanners._verify_image_file`.
- Produces: Safe login redirection, verified scam report upload processing.

- [ ] **Step 1: Write the failing test for open redirect and unverified upload**

Create `tests/test_auth_and_reports_security.py`:
```python
import os
import unittest
from io import BytesIO
from app_factory import create_app
from config import Config

class SecurityTestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

class TestAuthAndReportsSecurity(unittest.TestCase):
    def setUp(self):
        self.app = create_app(SecurityTestConfig)
        self.client = self.app.test_client()

    def test_open_redirect_rejected(self):
        # Register and login with next=https://evil.com
        self.client.post("/auth/register", data={
            "full_name": "Test User",
            "email": "test@example.com",
            "password": "Password123!",
            "confirm_password": "Password123!",
        })
        res = self.client.post("/auth/login?next=https://evil.com", data={
            "email": "test@example.com",
            "password": "Password123!",
        })
        self.assertNotIn("https://evil.com", res.headers.get("Location", ""))

    def test_scam_report_rejects_fake_png(self):
        fake_png = (BytesIO(b"<script>alert(1)</script>"), "payload.png")
        res = self.client.post("/api/submit-report", data={
            "title": "Fake Scam",
            "scam_type": "Lottery Scam",
            "description": "Scam description here",
            "screenshot": fake_png,
        }, content_type="multipart/form-data")
        self.assertEqual(res.status_code, 400)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests/test_auth_and_reports_security.py`  
Expected: FAIL (open redirect accepted to evil.com, fake PNG accepted).

- [ ] **Step 3: Implement open redirect guard and upload verification**

In `routes/auth.py`:
```python
from urllib.parse import urlsplit

def _is_safe_redirect(target: str | None) -> bool:
    if not target:
        return False
    parsed = urlsplit(target)
    # Target must be relative (no netloc) and not protocol-relative (not starting with //)
    return parsed.netloc == "" and not target.startswith("//") and target.startswith("/")

# Inside login():
next_page = request.args.get("next")
if not _is_safe_redirect(next_page):
    next_page = None
return redirect(next_page or url_for("dashboard.index"))
```

In `routes/reports.py`:
```python
from routes.scanners import _verify_image_file

# Inside submit_report():
if "screenshot" in request.files and request.files["screenshot"].filename:
    file = request.files["screenshot"]
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in current_app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return jsonify({"success": False, "error": "Unsupported file type."}), 400

    filename = f"report_{uuid.uuid4().hex[:10]}.{ext}"
    upload_dir = os.path.join(current_app.config["UPLOAD_FOLDER"], "screenshots")
    os.makedirs(upload_dir, exist_ok=True)
    full_path = os.path.join(upload_dir, filename)
    file.save(full_path)

    err = _verify_image_file(full_path)
    if err:
        if os.path.exists(full_path):
            os.remove(full_path)
        return jsonify({"success": False, "error": err}), 400

    screenshot_path = f"uploads/screenshots/{filename}"
```
Also handle `scam_date` parsing explicitly:
```python
if scam_date_str:
    try:
        scam_date = datetime.strptime(scam_date_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"success": False, "error": "Invalid scam date format. Expected YYYY-MM-DD."}), 400
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest tests/test_auth_and_reports_security.py`  
Expected: All tests pass.

- [ ] **Step 5: Commit**

```bash
git add routes/auth.py routes/reports.py tests/test_auth_and_reports_security.py
git commit -m "security: fix open redirect and enforce image verification on reports"
```

---

### Task 3: CSRF Protection & State Mutation on GET Elimination

**Files:**
- Modify: `requirements.txt`
- Modify: `app_factory.py:15-35`
- Modify: `routes/admin.py:182-190, 251-258`
- Modify: `templates/base.html`
- Modify: `templates/admin/blacklist.html`
- Modify: `templates/admin/messages.html`
- Modify: `static/js/main.js`
- Test: `tests/test_csrf_and_admin_security.py`

**Interfaces:**
- Consumes: `flask_wtf.csrf.CSRFProtect`.
- Produces: CSRF validation on all POST requests; secure POST endpoints for blacklist deletion and message status.

- [ ] **Step 1: Write test for CSRF enforcement and POST endpoint transitions**

Create `tests/test_csrf_and_admin_security.py`:
```python
import unittest
from app_factory import create_app
from config import Config
from models import db
from models.user import User

class CSRFTestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = True
    SECRET_KEY = "test-csrf-secret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

class TestCSRFProtection(unittest.TestCase):
    def setUp(self):
        self.app = create_app(CSRFTestConfig)
        self.client = self.app.test_client()

    def test_post_without_csrf_is_rejected(self):
        # A plain POST to login without CSRF token must fail with 400
        res = self.client.post("/auth/login", data={"email": "a@b.com", "password": "pass"})
        self.assertEqual(res.status_code, 400)

    def test_blacklist_delete_on_get_is_rejected(self):
        res = self.client.get("/admin/blacklist/1/delete")
        self.assertEqual(res.status_code, 405)  # Method Not Allowed
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests/test_csrf_and_admin_security.py`  
Expected: FAIL (CSRFProtect not installed / GET returns 302 redirect).

- [ ] **Step 3: Implement CSRF protection and update endpoints**

Add `Flask-WTF>=1.2.1` to `requirements.txt`.
In `app_factory.py`:
```python
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect()

def create_app(config_class=Config) -> Flask:
    ...
    csrf.init_app(app)
    # Exempt external scanner APIs from CSRF if needed, or attach headers in JS
    ...
```

In `routes/admin.py`:
Change `@admin_bp.route("/blacklist/<int:domain_id>/delete")` to `methods=["POST"]`.
Change `@admin_bp.route("/messages/<int:msg_id>/read")` to `methods=["POST"]`.

In `templates/base.html`:
Inject `<meta name="csrf-token" content="{{ csrf_token() }}">` into `<head>`.

In `static/js/main.js`:
Add CSRF header injection to `TrustLens.apiPost`:
```javascript
const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
// Add to fetch headers:
if (csrfToken) {
    headers['X-CSRFToken'] = csrfToken;
}
```

In `templates/admin/blacklist.html`:
Replace `<a href="{{ url_for('admin.blacklist_delete', domain_id=d.id) }}">` with:
```html
<form method="post" action="{{ url_for('admin.blacklist_delete', domain_id=d.id) }}" class="d-inline">
  <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
  <button type="submit" class="btn btn-ghost btn-sm-trust text-danger">Remove</button>
</form>
```

In `templates/admin/messages.html`:
Replace read link with a similar POST form.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest tests/test_csrf_and_admin_security.py`  
Expected: All tests pass.

- [ ] **Step 5: Commit**

```bash
git add requirements.txt app_factory.py routes/admin.py templates/ static/js/main.js tests/test_csrf_and_admin_security.py
git commit -m "security: enforce CSRF protection and convert state-mutating GETs to POST"
```

---

### Task 4: Database Safety, Schema Migration & Transaction Handlers

**Files:**
- Modify: `database/init_db.py:50-100`
- Modify: `routes/admin.py:388-660`
- Modify: `models/product_db.py:280-350`
- Test: `tests/test_db_safety_and_transactions.py`

**Interfaces:**
- Consumes: `sqlalchemy.engine.make_url`, `models.db.session`.
- Produces: Safe non-destructive schema reconciliation, atomic ID generation, transaction-safe admin routes.

- [ ] **Step 1: Write test for non-destructive schema drift and transaction rollbacks**

Create `tests/test_db_safety_and_transactions.py`:
```python
import unittest
from app_factory import create_app
from config import Config
from models import db
from models.admin import BlacklistedDomain

class DBSafetyTestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

class TestDBSafety(unittest.TestCase):
    def setUp(self):
        self.app = create_app(DBSafetyTestConfig)
        self.client = self.app.test_client()

    def test_schema_drift_does_not_drop_tables(self):
        from database.init_db import _verify_schema
        with self.app.app_context():
            # Add an extra column to blacklisted_domains
            with db.engine.begin() as conn:
                conn.execute(db.text("ALTER TABLE blacklisted_domains ADD COLUMN extra_test_col TEXT"))
            # Run schema verification
            _verify_schema(self.app)
            # Ensure table still exists and was not dropped
            count = BlacklistedDomain.query.count()
            self.assertEqual(count, 0)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests/test_db_safety_and_transactions.py`  
Expected: If `_drop_table` is active, it drops the table when extra columns are found (`removed = live_cols - model_cols`).

- [ ] **Step 3: Implement non-destructive schema reconciliation and admin rollbacks**

In `database/init_db.py`:
```python
from sqlalchemy.engine import make_url

def _ensure_database(app) -> None:
    uri = app.config["SQLALCHEMY_DATABASE_URI"]
    if uri.startswith("sqlite"):
        ...
        return

    if uri.startswith("mysql"):
        try:
            import pymysql
            url = make_url(uri)
            connection = pymysql.connect(
                host=url.host or "localhost",
                user=url.username or "root",
                password=url.password or "",
                port=url.port or 3306,
            )
            cursor = connection.cursor()
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{url.database}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
            cursor.close()
            connection.close()
        except Exception as exc:
            app.logger.warning("Could not auto-create MySQL database: %s", exc)

def _verify_schema(app) -> None:
    ...
    if added and not removed:
        _add_missing_columns(app, table, added)
    elif removed:
        app.logger.warning(
            "Table '%s' contains extra/drifted columns (%s). Skipping auto-drop to prevent data loss.",
            table.name, removed
        )
```

In `routes/admin.py`:
Add UUID component to `_generate_product_id`:
```python
import uuid

def _generate_product_id(brand_name: str, product_name: str) -> str:
    base = "PRD-" + _norm(f"{brand_name} {product_name}").upper()[:30]
    token = uuid.uuid4().hex[:6].upper()
    return f"{base}-{token}"
```
Wrap `product_new`, `product_edit`, `product_delete`, `ingredient_add`, `ingredient_delete`, `category_add`, `category_delete` in `try...except Exception:` blocks with `db.session.rollback()`.

In `models/product_db.py`:
Add `cascade="all, delete-orphan"` to `Product.identifiers`, `Product.images`, `Product.attributes`, `Product.verifications`, and `Product.score_factors`.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest tests/test_db_safety_and_transactions.py`  
Expected: All tests pass.

- [ ] **Step 5: Commit**

```bash
git add database/init_db.py routes/admin.py models/product_db.py tests/test_db_safety_and_transactions.py
git commit -m "fix(db): eliminate auto-drop schema destruction and add transaction rollbacks"
```

---

### Task 5: Email Scanner Scoring Semantics Normalization

**Files:**
- Modify: `services/email_scanner.py:1280-1340`
- Modify: `templates/scanners/email_scanner.html:45-75`
- Modify: `tests/test_email_scanner.py:25-50`
- Test: `tests/test_email_scanner.py`

**Interfaces:**
- Consumes: `services.email_scanner.scan_email`.
- Produces: Normalized `score` (Trust Score 0-100) and `risk_score` (Risk 0-100).

- [ ] **Step 1: Write test for normalized email trust score**

Add assertion in `tests/test_email_scanner.py`:
```python
def test_safe_email_has_high_trust_score():
    safe_sample = "From: hr@trusted.com\nSubject: Meeting\nHi team, let us meet tomorrow at 10am."
    result = scan_email(safe_sample)
    assert result["score"] >= 80  # Trust Score must be >= 80 for safe emails
    assert result["risk_score"] <= 20
    assert result["status"] == "safe"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests/test_email_scanner.py`  
Expected: FAIL (`result["score"]` was returning ~6 risk instead of >=80 trust).

- [ ] **Step 3: Normalize email scanner output and persist values**

In `services/email_scanner.py`:
```python
# Around line 1285:
trust_score = max(0, min(100, 100 - risk))

result = {
    "score": trust_score,
    "risk_score": risk,
    "status": cat["status"],
    "category": cat["category"],
    "risk_label": cat["label"],
    "risk_emoji": cat["emoji"],
    "confidence": confidence,
    ...
}

# In persist_scan():
scan = EmailScan(
    user_id=user_id,
    email_content=content[:2000],
    trust_score=payload["score"],  # now accurately persists Trust Score (high = safe)
    status=payload["status"],
    ...
)
```

In `templates/scanners/email_scanner.html`:
Update `renderResult(data)`:
```javascript
TrustLens.renderGauge(document.getElementById("gauge"), data.score, "TRUST SCORE");
```

In `tests/test_email_scanner.py`:
Update test regression band helpers to test `result["risk_score"]` for backward compatibility with the existing test matrix.

- [ ] **Step 4: Run test to verify it passes**

Run: `python tests/test_email_scanner.py`  
Expected: PASS (all samples A-L match expected bands).

- [ ] **Step 5: Commit**

```bash
git add services/email_scanner.py templates/scanners/email_scanner.html tests/test_email_scanner.py
git commit -m "fix(email): normalize score to 0-100 Trust Score and export explicit risk_score"
```

---

### Task 6: Concurrency, QR Classification & Idempotent Dashboard

**Files:**
- Modify: `services/whatsapp_scanner.py:79-98`
- Modify: `services/qr_scanner.py:603-615`
- Modify: `routes/dashboard.py:40-75`
- Test: `tests/test_scanners_logic_and_dashboard.py`

**Interfaces:**
- Consumes: `services.whatsapp_scanner.extract_text_ocr`, `services.qr_scanner.scan_qr_image`.
- Produces: Unblocked timeout handling, neutral QR failure verdict, idempotent dashboard notifications.

- [ ] **Step 1: Write tests for unblocked timeout and neutral QR classification**

Create `tests/test_scanners_logic_and_dashboard.py`:
```python
import unittest
from services.qr_scanner import scan_qr_image
from app_factory import create_app
from config import Config

class LogicTestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

class TestScannersLogic(unittest.TestCase):
    def setUp(self):
        self.app = create_app(LogicTestConfig)

    def test_missing_qr_is_unverifiable_not_dangerous(self):
        import tempfile
        from PIL import Image
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            Image.new("RGB", (100, 100), color="white").save(f.name)
            temp_path = f.name
        try:
            result = scan_qr_image(temp_path)
            self.assertNotEqual(result["status"], "dangerous")
            self.assertEqual(result["verdict"], "No QR Code Detected")
        finally:
            import os
            os.remove(temp_path)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests/test_scanners_logic_and_dashboard.py`  
Expected: FAIL (missing QR returns `status="dangerous"` and `score=0`).

- [ ] **Step 3: Implement fixes**

In `services/whatsapp_scanner.py:extract_text_ocr()`:
```python
try:
    reader = _get_reader()
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

In `services/qr_scanner.py:scan_qr_image()`:
```python
if not payloads:
    return {
        "score": 50,
        "status": "warning",
        "qr_type": "none",
        "verdict": "No QR Code Detected",
        "reasons": [{"severity": "info", "text": "No QR code could be detected or decoded in the image."}],
        "decoded_url": None,
        "decode": decode_report,
        "processing_time_ms": int((time.perf_counter() - start) * 1000),
    }
```

In `routes/dashboard.py`:
Remove lines 64-72 mutating `reply.is_viewed = True` during `GET /dashboard`.
Add endpoint:
```python
@dashboard_bp.route("/api/reports/<int:report_id>/mark-viewed", methods=["POST"])
@login_required
def mark_report_viewed(report_id):
    report = ScamReport.query.filter_by(id=report_id, user_id=current_user.id).first()
    if report:
        for reply in report.replies:
            reply.is_viewed = True
        db.session.commit()
    return jsonify({"success": True})
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest tests/test_scanners_logic_and_dashboard.py`  
Expected: All tests pass.

- [ ] **Step 5: Commit**

```bash
git add services/whatsapp_scanner.py services/qr_scanner.py routes/dashboard.py tests/test_scanners_logic_and_dashboard.py
git commit -m "fix(logic): fix OCR timeout lockup, classify missing QR safely, and make dashboard GET idempotent"
```

---

### Task 7: Performance Optimization (Analytics Grouping & Unified Dashboard)

**Files:**
- Modify: `services/analytics.py:32-100`
- Modify: `routes/admin.py:291-300`
- Modify: `routes/dashboard.py:40-60`
- Modify: `templates/dashboard.html:40-70`
- Test: `tests/test_analytics_and_dashboard_perf.py`

**Interfaces:**
- Consumes: SQL `group_by`, SQL `func.count`.
- Produces: Fast aggregated timeseries, indexed ingredient matching, multi-scanner dashboard feed.

- [ ] **Step 1: Write test for fast analytics aggregation and unified recent scans**

Create `tests/test_analytics_and_dashboard_perf.py`:
```python
import unittest
from app_factory import create_app
from config import Config
from services.analytics import scan_volume_timeseries, fraud_type_counts

class PerfTestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

class TestAnalyticsPerformance(unittest.TestCase):
    def setUp(self):
        self.app = create_app(PerfTestConfig)

    def test_timeseries_returns_14_days(self):
        with self.app.app_context():
            series = scan_volume_timeseries(14)
            self.assertEqual(len(series), 14)
            self.assertIn("date", series[0])
            self.assertIn("count", series[0])
```

- [ ] **Step 2: Run test to verify current output**

Run: `python -m unittest tests/test_analytics_and_dashboard_perf.py`  
Expected: Passes but executes 112 queries.

- [ ] **Step 3: Implement optimized queries and unified dashboard recent scans**

In `services/analytics.py`:
```python
def scan_volume_timeseries(days: int = 14) -> list:
    start_date = datetime.utcnow().date() - timedelta(days=days - 1)
    start_dt = datetime(start_date.year, start_date.month, start_date.day)

    # Initialize zero counts for each day
    day_counts = {
        (start_date + timedelta(days=offset)).isoformat(): 0
        for offset in range(days)
    }

    # Group by date per model in 8 queries instead of 112
    for m in SCAN_MODELS:
        date_col = db.func.date(m.created_at)
        results = (
            db.session.query(date_col, db.func.count(m.id))
            .filter(m.created_at >= start_dt)
            .group_by(date_col)
            .all()
        )
        for date_str, count in results:
            if date_str in day_counts:
                day_counts[date_str] += count

    return [{"date": d, "count": day_counts[d]} for d in sorted(day_counts.keys())]

def fraud_type_counts() -> list:
    counts = {}
    # Use SQL group by for scam reports
    report_counts = (
        db.session.query(ScamReport.scam_type, db.func.count(ScamReport.id))
        .group_by(ScamReport.scam_type)
        .all()
    )
    for scam_type, count in report_counts:
        key = (scam_type or "Other").strip() or "Other"
        counts[key] = counts.get(key, 0) + count

    # Categorical scanner additions
    counts["Website/Phishing"] = counts.get("Website/Phishing", 0) + WebsiteScan.query.count()
    counts["Email/Phishing"] = counts.get("Email/Phishing", 0) + EmailScan.query.count()
    counts["Payment Fraud"] = counts.get("Payment Fraud", 0) + PaymentScan.query.count()
    counts["QR Code Scam"] = counts.get("QR Code Scam", 0) + QRScan.query.count()
    counts["Fake Job/Internship"] = counts.get("Fake Job/Internship", 0) + JobScan.query.count()
    counts["Product/Ingredient"] = counts.get("Product/Ingredient", 0) + ProductScan.query.count()
    counts["Misleading Claim"] = counts.get("Misleading Claim", 0) + ClaimScan.query.count()

    return sorted(counts.items(), key=lambda item: item[1], reverse=True)
```

In `routes/admin.py`:
In `_resolve_ingredient(name: str)`:
```python
def _resolve_ingredient(name: str):
    if not name:
        return None
    target = _norm(name)
    # Check exact normalized match first via index
    ing = Ingredient.query.filter_by(normalized_name=target).first()
    if ing:
        return ing
    # Only search aliases if exact normalized name didn't match
    for candidate in Ingredient.query.filter(Ingredient.aliases.isnot(None)).all():
        if any(_norm(a) == target for a in (candidate.aliases or [])):
            return candidate
    return None
```

In `routes/dashboard.py`:
Aggregate recent scans across models:
```python
recent_scans = []
for m, scan_label, target_attr in (
    (WebsiteScan, "Website", "url"),
    (JobScan, "Job", "company_name"),
    (EmailScan, "Email", "email_content"),
    (QRScan, "QR Code", "decoded_url"),
    (PaymentScan, "Payment", "screenshot_path"),
    (ProductScan, "Product", "product_name"),
    (ClaimScan, "Claim", "claim_text"),
):
    items = m.query.order_by(m.created_at.desc()).limit(5).all()
    for item in items:
        recent_scans.append({
            "type": scan_label,
            "target": (getattr(item, target_attr) or "-")[:40],
            "trust_score": item.trust_score,
            "status": item.status,
            "created_at": item.created_at,
        })
recent_scans = sorted(recent_scans, key=lambda s: s["created_at"], reverse=True)[:8]
```
Update `templates/dashboard.html` to display the scan `Type` and `Target`.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest tests/test_analytics_and_dashboard_perf.py`  
Expected: All tests pass.

- [ ] **Step 5: Commit**

```bash
git add services/analytics.py routes/admin.py routes/dashboard.py templates/dashboard.html tests/test_analytics_and_dashboard_perf.py
git commit -m "perf: optimize analytics with SQL GROUP BY, index ingredient lookups, and unify dashboard recent scans"
```

---

### Task 8: Full Regression & System Verification

**Files:**
- Modify: `models/user.py`, `models/scan.py`, `models/report.py` (replace deprecated `datetime.utcnow` with `datetime.now(timezone.utc)`)
- Test: All test suites in `tests/`

- [ ] **Step 1: Replace deprecated `datetime.utcnow` usages**

Update timestamp defaults across models to use `lambda: datetime.now(timezone.utc)`.

- [ ] **Step 2: Run all test suites across the repository**

Run:
```bash
python -m unittest discover tests/
python tests/test_email_scanner.py
python tests/test_claim_scanner.py
python tests/test_payment_scanner.py
python tests/test_product_scanner.py
```
Expected: All tests pass cleanly without errors.

- [ ] **Step 3: Final verification commit**

```bash
git add models/
git commit -m "refactor: replace deprecated datetime.utcnow and verify full regression suite"
```

