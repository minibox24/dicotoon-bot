from bot import DicoToon
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

bot = DicoToon()

bot.run(BOT_TOKEN)
