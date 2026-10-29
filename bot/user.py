#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pyrogram import Client, __version__

from . import API_HASH, APP_ID, LOGGER


class User(Client):
    def __init__(self):
        super().__init__(
            "userbot",
            api_hash=API_HASH,
            api_id=APP_ID,
            bot_token=None,
            workers=20
        )
        self.LOGGER = LOGGER

    async def start(self):
        await super().start()
        return None

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info("User client stopped.")
