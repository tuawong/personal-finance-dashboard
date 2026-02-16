# Simple config.py (your project scale)
from dotenv import load_dotenv
import os

load_dotenv()

DB_PATH = os.getenv('DB_PATH')
if not DB_PATH:
    raise ValueError("DB_PATH is required")