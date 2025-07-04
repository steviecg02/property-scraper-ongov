# config.py
import logging
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
HEADLESS = os.getenv("HEADLESS", "True") == "True"
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG").upper()

logger = logging.getLogger("scraper")
logger.setLevel(getattr(logging, LOG_LEVEL, logging.DEBUG))

handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s'))
logger.addHandler(handler)
logger.propagate = False

# Reduce noise from noisy modules unless overridden
for noisy in ("urllib3", "asyncio", "playwright"):
    logging.getLogger(noisy).setLevel(logging.WARNING)
