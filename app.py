"""
TrustLens - AI Based Information Verification System
Entry point. Builds the Flask application via the factory pattern.

Run with:
    python app.py
"""

import os
import urllib.parse
from app_factory import create_app


class VercelPathMiddleware:
    """
    Middleware that normalizes PATH_INFO when Vercel rewrites requests
    through /api/index.py or passes original request paths in query parameters or headers.
    """

    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        query_string = environ.get("QUERY_STRING", "")
        params = urllib.parse.parse_qs(query_string, keep_blank_values=True)

        if "__path__" in params and params["__path__"]:
            target_path = params["__path__"][0]
            if not target_path.startswith("/"):
                target_path = "/" + target_path
            environ["PATH_INFO"] = target_path

            del params["__path__"]
            new_qs = urllib.parse.urlencode([(k, v) for k, vs in params.items() for v in vs])
            environ["QUERY_STRING"] = new_qs
        else:
            forwarded = (
                environ.get("HTTP_X_FORWARDED_PATH")
                or environ.get("HTTP_X_FORWARDED_URI")
                or environ.get("HTTP_X_REAL_PATH")
                or environ.get("HTTP_X_INVOKE_PATH")
                or environ.get("HTTP_X_MATCHED_PATH")
            )
            path = environ.get("PATH_INFO", "")
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
