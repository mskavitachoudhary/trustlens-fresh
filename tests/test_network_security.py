import unittest
from services.network_security import validate_public_url


class TestNetworkSecurity(unittest.TestCase):
    def test_blocks_private_and_loopback_ips(self):
        self.assertFalse(validate_public_url("http://127.0.0.1:5000")[0])
        self.assertFalse(validate_public_url("http://localhost:8080")[0])
        self.assertFalse(validate_public_url("http://10.0.0.1")[0])
        self.assertFalse(validate_public_url("http://192.168.1.1")[0])
        self.assertFalse(validate_public_url("http://172.16.0.1")[0])
        self.assertFalse(validate_public_url("http://169.254.169.254/latest/meta-data/")[0])

    def test_blocks_invalid_schemes(self):
        self.assertFalse(validate_public_url("file:///etc/passwd")[0])
        self.assertFalse(validate_public_url("ftp://example.com")[0])
        self.assertFalse(validate_public_url("gopher://example.com")[0])

    def test_allows_public_domains(self):
        # Public IP directly
        is_valid, _ = validate_public_url("https://8.8.8.8")
        self.assertTrue(is_valid)

        # Public domain with mocked DNS
        from unittest.mock import patch
        with patch("socket.getaddrinfo", return_value=[(None, None, None, None, ("93.184.216.34", 443))]):
            is_valid, _ = validate_public_url("https://example.com")
            self.assertTrue(is_valid)

    def test_blocks_domain_resolving_to_private_ip(self):
        from unittest.mock import patch
        with patch("socket.getaddrinfo", return_value=[(None, None, None, None, ("127.0.0.1", 80))]):
            is_valid, reason = validate_public_url("http://attacker.com")
            self.assertFalse(is_valid)
            self.assertIn("private/restricted IP", reason)


if __name__ == "__main__":
    unittest.main()
