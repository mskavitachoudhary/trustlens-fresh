from __future__ import annotations

import os
import unittest
from io import BytesIO
from app_factory import create_app
from config import Config
from models import db


class SecurityTestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class TestAuthAndReportsSecurity(unittest.TestCase):
    def setUp(self):
        self.app = create_app(SecurityTestConfig)
        self.client = self.app.test_client()

    def test_open_redirect_rejected(self):
        # Register user
        self.client.post("/auth/register", data={
            "full_name": "Test User",
            "email": "test@example.com",
            "password": "Password123!",
            "confirm_password": "Password123!",
        })
        # Attempt login with external next URL
        res = self.client.post("/auth/login?next=https://evil.com", data={
            "email": "test@example.com",
            "password": "Password123!",
        })
        self.assertNotIn("evil.com", res.headers.get("Location", ""))
        self.assertIn("/dashboard", res.headers.get("Location", ""))

    def test_protocol_relative_redirect_rejected(self):
        self.client.post("/auth/register", data={
            "full_name": "Test User 2",
            "email": "test2@example.com",
            "password": "Password123!",
            "confirm_password": "Password123!",
        })
        res = self.client.post("/auth/login?next=//evil.com", data={
            "email": "test2@example.com",
            "password": "Password123!",
        })
        self.assertNotIn("evil.com", res.headers.get("Location", ""))
        self.assertIn("/dashboard", res.headers.get("Location", ""))

    def test_scam_report_rejects_fake_png(self):
        fake_png = (BytesIO(b"<script>alert(1)</script>"), "payload.png")
        res = self.client.post("/api/submit-report", data={
            "title": "Fake Scam",
            "scam_type": "Lottery Scam",
            "description": "Scam description here",
            "screenshot": fake_png,
        }, content_type="multipart/form-data")
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertFalse(data["success"])
        self.assertIn("error", data)

    def test_scam_report_rejects_invalid_date(self):
        res = self.client.post("/api/submit-report", data={
            "title": "Date Scam",
            "scam_type": "Investment Scam",
            "description": "Scam description here",
            "scam_date": "not-a-date",
        })
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertFalse(data["success"])
        self.assertIn("date", data["error"].lower())


if __name__ == "__main__":
    unittest.main()

