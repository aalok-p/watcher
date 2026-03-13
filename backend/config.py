import os
from dotenv import load_dotenv

load_dotenv()

POLL_INTERVAL_SEC = float(os.getenv("POLL_INTERVAL_SEC", "3"))
SCREENSHOT_ENABLED = os.getenv("SCREENSHOT_ENABLED", "true").lower() == "true"
PORT = int(os.getenv("PORT", "8000"))

# LM_STUDIO_URL = os.getenv("LM_STUDIO_URL", "http://localhost:1234")
# LM_STUDIO_MODEL = os.getenv("LM_STUDIO_MODEL", "local-model")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "your model")
