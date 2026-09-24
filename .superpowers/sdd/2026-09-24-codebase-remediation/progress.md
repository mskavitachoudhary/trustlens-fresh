# SDD ledger — plan: docs/superpowers/plans/2026-09-24-codebase-remediation.md

## Pre-flight
- 8 tasks, interfaces aligned with spec: Complete.

## Completed Tasks
- [x] **Task 1: SSRF Guard & Response Limit**: Added `services/network_security.py` with private IP/loopback filtering and streaming body limit. Wired into `website_scanner.py` and `job_scanner.py`. Verified via `tests/test_network_security.py`.
- [x] **Task 2: Open Redirect & File Upload Validation**: Added `_is_safe_redirect` in `routes/auth.py`. Added Pillow image format and payload validation plus safe date parsing in `routes/reports.py`. Verified via `tests/test_auth_and_reports_security.py`.
- [x] **Task 3: CSRF Protection & State Mutation on GET Elimination**: Added `Flask-WTF` CSRF protection with tokens in base layout and AJAX interceptor. Replaced unsafe GET mutation routes (`/admin/blacklist/<id>/delete` and `/admin/messages/<id>/read`) with POST and updated admin templates. Verified via `tests/test_csrf_and_admin_security.py`.
- [x] **Task 4: Database Safety, Schema Migration & Transaction Handlers**: Replaced destructive `_drop_table()` in `database/init_db.py` with non-destructive table validation and `make_url()`. Added rollback handlers to admin mutation routes and unique collision handling. Verified via `tests/test_db_safety_and_transactions.py`.
- [x] **Task 5: Email Scanner Trust Score Normalization**: Inverted score semantics in `services/email_scanner.py` (`trust_score = 100 - risk_score`) to match TrustLens standard. Updated gauge presentation and unit tests. Verified via `tests/test_email_scanner.py`.
- [x] **Task 6: Concurrency, QR Classification & Idempotent Dashboard**: Added unblocked worker timeouts in `services/whatsapp_scanner.py`. Cleaned zxing-cpp parameters and added honest neutral scoring (50 warning) on unreadable QR codes in `services/qr_scanner.py`. Made `GET /dashboard` idempotent and added `POST /api/reports/<id>/mark-viewed`. Verified via `tests/test_scanners_logic_and_dashboard.py`.
- [x] **Task 7: Performance Optimization (Analytics SQL Grouping & Unified Dashboard)**: Replaced Python loops in `services/analytics.py` with SQL `GROUP BY` and `db.func.date`. Optimized ingredient alias lookups in `routes/admin.py`. Unified scan history in `routes/dashboard.py`. Verified via `tests/test_analytics_and_dashboard_perf.py`.
- [x] **Task 8: Full Regression & System Verification**: Replaced all deprecated `datetime.utcnow()` across models and services with `utc_now()`. Pinned `zxing-cpp==2.1.0`. Fixed QR empty payload index error in payment scanner. Added missing `PRD-DETTOL-ANTISEPTIC-IN` and variant logic in product database. Verified entire regression test suite (100% pass across all tests).
