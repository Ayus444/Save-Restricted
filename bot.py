# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

from pyrogram import Client
from pyrogram.errors import FloodWait
import asyncio
from config import API_ID, API_HASH, BOT_TOKEN

class Bot(Client):

    def __init__(self):
        super().__init__(
            "techvj login",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins=dict(root="TechVJ"),
            workers=50,
            sleep_threshold=10
        )

    async def start(self, **kwargs):  # Accept extra args like use_qr
        try:
            await super().start(**kwargs)
            print('Bot Started Powered By @VJ_Botz')
        except FloodWait as e:
            print(f"FloodWait: Sleeping for {e.value} seconds...")
            await asyncio.sleep(e.value)
            await self.start(**kwargs)

    async def stop(self, *args):
        await super().stop()
        print('Bot Stopped Bye')

Bot().run()
