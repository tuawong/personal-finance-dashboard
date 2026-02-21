# Simple config.py (your project scale)
from dotenv import load_dotenv
import os

load_dotenv()

DB_PATH = os.getenv('DB_PATH')
if not DB_PATH:
    raise ValueError("DB_PATH is required")

RAW_DATA_PATH = os.getenv('RAW_DATA_PATH')
if not RAW_DATA_PATH:
    raise ValueError("RAW_DATA_PATH is required")

API_KEY_OPENAI = os.getenv('API_KEY_OPENAI')
if not API_KEY_OPENAI:
    raise ValueError("API_KEY_OPENAI is required")