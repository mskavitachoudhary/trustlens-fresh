from __future__ import annotations

import os
import tempfile
import unittest
from PIL import Image
from app_factory import create_app
from config import Config
from models import db
from models.user import User
from models.report import ScamReport, ScamReportReply
from services.qr_scanner import scan_qr_image


class LogicTestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class TestScannersLogicAndDashboard(unittest.TestCase):
    def setUp(self):
        self.app = create_app(LogicTestConfig)
        self.client = self.app.test_client()

    def test_missing_qr_is_warning_not_dangerous(self):
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            Image.new("RGB", (100, 100), color="white").save(f.name)
            temp_path = f.name
        try:
            result = scan_qr_image(temp_path)
            self.assertNotEqual(result["status"], "dangerous")
            self.assertEqual(result["status"], "warning")
            self.assertEqual(result["score"], 50)
            self.assertEqual(result["verdict"], "No QR Code Detected")
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_dashboard_get_is_idempotent(self):
        with self.app.app_context():
            user = User(full_name="Dash User", email="dash@example.com", role="user")
            user.set_password("Password123!")
            db.session.add(user)
            db.session.commit()

            report = ScamReport(
                user_id=user.id,
                title="Test Scam",
                scam_type="Lottery Scam",
                description="desc",
            )
            db.session.add(report)
            db.session.flush()

            reply = ScamReportReply(
                report_id=report.id,
                admin_message="Under review",
                status_after="under review",
                is_viewed=False,
            )
            db.session.add(reply)
            db.session.commit()
            report_id = report.id
            reply_id = reply.id

        # Login
        self.client.post("/auth/login", data={"email": "dash@example.com", "password": "Password123!"})

        # First GET /dashboard
        res1 = self.client.get("/dashboard")
        self.assertEqual(res1.status_code, 200)

        # Check that reply was NOT marked as viewed by GET
        with self.app.app_context():
            r = db.session.get(ScamReportReply, reply_id)
            self.assertFalse(r.is_viewed)

        # Second GET /dashboard
        res2 = self.client.get("/dashboard")
        self.assertEqual(res2.status_code, 200)

        with self.app.app_context():
            r = db.session.get(ScamReportReply, reply_id)
            self.assertFalse(r.is_viewed)

        # Call POST mark-viewed endpoint
        res3 = self.client.post(f"/api/reports/{report_id}/mark-viewed")
        self.assertEqual(res3.status_code, 200)
        self.assertTrue(res3.get_json()["success"])

        # Check that reply IS now marked as viewed
        with self.app.app_context():
            r = db.session.get(ScamReportReply, reply_id)
            self.assertTrue(r.is_viewed)


if __name__ == "__main__":
    unittest.main()
