import os
import sys

# Ensure root directory is on sys.path so app_factory and all modules import cleanly
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app_factory import create_app

# Vercel serverless WSGI entry point
app = create_app()
