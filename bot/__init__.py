#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import time
from logging.handlers import RotatingFileHandler

from .translation import Translation


def _required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(
            f"Missing required environment variable: {name}. "
            "Add it in Render Dashboard > your service > Environment."
        )
    return value


APP_ID = int(_required_env("APP_ID"))
API_HASH = _required_env("API_HASH")
BOT_TOKEN = _required_env("BOT_TOKEN")
DB_URI = _required_env("DB_URI")

VERIFY = {}

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        RotatingFileHandler("autofilterbot.txt", maxBytes=50000000, backupCount=10),
        logging.StreamHandler(),
    ],
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

start_uptime = time.time()


def LOGGER(name: str) -> logging.Logger:
    return logging.getLogger(name)
