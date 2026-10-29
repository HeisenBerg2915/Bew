#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pyrogram import Client, enums

from . import API_HASH, APP_ID, LOGGER, BOT_TOKEN


class Bot(Client):
    def __init__(self):
        super().__init__(
            name="bot",
            api_id=APP_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins={"root": "bot/plugins"},
            workers=200,
            sleep_threshold=10,
        )

    async def start(self):
        await super().start()
        me = await self.get_me()
        self.set_parse_mode(enums.ParseMode.HTML)
        LOGGER(__name__).info(
            f"Bot started successfully: @{me.username}"
        )

    async def stop(self, *args):
        await super().stop()
        LOGGER(__name__).info("Bot stopped.")
