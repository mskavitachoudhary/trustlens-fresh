"""
TrustLens - AI Based Information Verification System
Entry point. Builds the Flask application via the factory pattern.

Run with:
    python app.py
"""

import os
from app_factory import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
