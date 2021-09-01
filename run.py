from bot import DicoToon
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
DB_URL = os.environ.get("DB_URL")

bot = DicoToon(DB_URL)

bot.run(BOT_TOKEN)
