"""
TrustLens - AI Based Information Verification System
Entry point. Builds the Flask application via the factory pattern.

Run with:
    python app.py
"""

import os
from app_factory import create_app

class VercelPathMiddleware:
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        path = environ.get("PATH_INFO", "")
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


app = create_app()
app.wsgi_app = VercelPathMiddleware(app.wsgi_app)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
