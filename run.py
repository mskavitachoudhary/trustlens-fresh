"""
TrustLens - AI Based Information Verification System
Development launcher. Run `python run.py` for the dev server.
"""

import os
from app_factory import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="127.0.0.1", port=port, debug=True)
