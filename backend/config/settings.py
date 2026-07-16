


# backend/config/settings.py
import os
from dotenv import load_dotenv

# Absolute project root
BACKEND_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BACKEND_DIR, ".."))
ROOT_DB_DIR = os.path.join(PROJECT_ROOT, "db")

# Hardcode root db path, ignore .env DB_PATH completely
DB_PATH = os.path.join(ROOT_DB_DIR, "agent.db")
KLINE_DB_PATH = os.path.join(ROOT_DB_DIR, "ashare_kline.db")

# Load env only for llm config, skip DB_PATH
env_path = os.path.join(BACKEND_DIR, ".env")
load_dotenv(dotenv_path=env_path, override=False)

# LLM config
MODEL_NAME = os.getenv("MODEL_NAME", "hermes3:8b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
MAX_HISTORY_TOKENS = int(os.getenv("MAX_HISTORY_TOKENS", 4096))
STREAM_OUTPUT = os.getenv("STREAM_OUTPUT", "true") == "true"
MODEL_THRESHOLD = float(os.getenv("MODEL_THRESHOLD", 0.62))
