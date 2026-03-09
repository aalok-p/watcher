import os
from dotenv import load_dotenv

load_dotenv()

POLL_INTERVAL_SEC = float(os.getenv("POLL_INTERVAL_SEC", "3"))
SCREENSHOT_ENABLED = os.getenv("SCREENSHOT_ENABLED", "true").lower() == "true"
PORT = int(os.getenv("PORT", "8000"))
