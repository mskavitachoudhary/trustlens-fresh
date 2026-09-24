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

    try:
        parsed = urlsplit(url)
    except Exception as exc:
        return False, f"Malformed URL: {exc}"

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
        port = parsed.port or (443 if parsed.scheme.lower() == "https" else 80)
        addr_info = socket.getaddrinfo(host, port, proto=socket.IPPROTO_TCP)
        for item in addr_info:
            sockaddr = item[4]
            ip_str = sockaddr[0]
            ip = ipaddress.ip_address(ip_str)
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
                return False, f"Domain {host} resolves to private/restricted IP ({ip_str})."
    except socket.gaierror:
        # If running offline or domain does not resolve, let caller handle or report
        return False, f"Could not resolve domain: {host}"
    except Exception as exc:
        return False, f"DNS validation error: {str(exc)}"

    return True, ""

