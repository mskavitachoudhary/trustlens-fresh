from __future__ import annotations

import unittest
from app_factory import create_app
from config import Config
from models import db
from models.user import User
from models.scan import WebsiteScan, JobScan
from models.report import ScamReport
from services.analytics import scan_volume_timeseries, user_growth_timeseries, fraud_type_counts


class PerfTestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class TestAnalyticsPerformance(unittest.TestCase):
    def setUp(self):
        self.app = create_app(PerfTestConfig)
        self.client = self.app.test_client()

    def test_timeseries_returns_14_days(self):
        with self.app.app_context():
            # Add some scans
            w = WebsiteScan(url="https://example.com", trust_score=90, status="safe")
            j = JobScan(company_name="Acme Corp", trust_score=85, status="safe")
            db.session.add_all([w, j])
            db.session.commit()

            series = scan_volume_timeseries(14)
            self.assertEqual(len(series), 14)
            self.assertIn("date", series[0])
            self.assertIn("count", series[0])
            total_scans = sum(item["count"] for item in series)
            self.assertGreaterEqual(total_scans, 2)

    def test_user_growth_timeseries(self):
        with self.app.app_context():
            growth = user_growth_timeseries(14)
            self.assertEqual(len(growth), 14)
            self.assertIn("date", growth[0])
            self.assertIn("count", growth[0])
            # Bootstrap admin was created today
            today_count = growth[-1]["count"]
            self.assertGreaterEqual(today_count, 1)

    def test_fraud_type_counts(self):
        with self.app.app_context():
            r = ScamReport(title="Lottery win", scam_type="Lottery Scam", description="details")
            db.session.add(r)
            db.session.commit()

            fraud = fraud_type_counts()
            self.assertTrue(any(label == "Lottery Scam" and count >= 1 for label, count in fraud))

    def test_dashboard_renders_unified_scans(self):
        with self.app.app_context():
            user = User(full_name="Unified User", email="unified@example.com", role="user")
            user.set_password("Password123!")
            db.session.add(user)
            w = WebsiteScan(url="https://site.org", trust_score=88, status="safe")
            j = JobScan(company_name="Tech Co", trust_score=30, status="dangerous")
            db.session.add_all([w, j])
            db.session.commit()

        self.client.post("/auth/login", data={"email": "unified@example.com", "password": "Password123!"})
        res = self.client.get("/dashboard")
        self.assertEqual(res.status_code, 200)
        html = res.get_data(as_text=True)
        self.assertIn("Website", html)
        self.assertIn("Job", html)
        self.assertIn("site.org", html)
        self.assertIn("Tech Co", html)


if __name__ == "__main__":
    unittest.main()

