"""
Aegis AI
Module: Logger
Version: 1.0.0
"""

import logging
import os

# Create logs folder if it doesn't exist
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("logs/aegis.log"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger("AegisAI")