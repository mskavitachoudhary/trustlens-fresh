from __future__ import annotations

import unittest
from app_factory import create_app
from config import Config
from models import db
from models.user import User


class CSRFTestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = True
    SECRET_KEY = "test-csrf-secret-key-12345"
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

    def test_message_mark_read_on_get_is_rejected(self):
        res = self.client.get("/admin/messages/1/read")
        self.assertEqual(res.status_code, 405)  # Method Not Allowed


if __name__ == "__main__":
    unittest.main()

