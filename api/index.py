"""
Vercel Serverless Function Entry Point for TrustLens.
Handles request path normalization across Vercel WSGI rewrites.
"""
import os
import sys

# Ensure root directory is on sys.path so app_factory and all modules import cleanly
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app_factory import create_app


class VercelPathMiddleware:
    """
    Middleware that normalizes PATH_INFO when Vercel rewrites requests
    through /api/index.py or passes original request paths in headers.
    """

    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        path = environ.get("PATH_INFO", "")

        # Check if Vercel provided the real requested URI in proxy headers
        forwarded = (
            environ.get("HTTP_X_FORWARDED_PATH")
            or environ.get("HTTP_X_FORWARDED_URI")
            or environ.get("HTTP_X_REAL_PATH")
            or environ.get("REQUEST_URI")
        )
        if forwarded and not forwarded.startswith("/api/index.py") and not forwarded.startswith("/api/index"):
            environ["PATH_INFO"] = forwarded.split("?")[0]
        elif path.startswith("/api/index.py"):
            rest = path[len("/api/index.py"):]
            environ["PATH_INFO"] = rest if rest else "/"
        elif path.startswith("/api/index"):
            rest = path[len("/api/index"):]
            environ["PATH_INFO"] = rest if rest else "/"

        return self.wsgi_app(environ, start_response)


flask_app = create_app()
flask_app.wsgi_app = VercelPathMiddleware(flask_app.wsgi_app)

# Vercel serverless WSGI entry point
app = flask_app
