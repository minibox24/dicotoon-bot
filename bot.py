from discord.ext.commands import Bot
from tortoise import Tortoise


class DicoToon(Bot):
    def __init__(self, db_url, *args, **kwargs):
        if not kwargs.get("command_prefix"):
            kwargs["command_prefix"] = "!"

        super().__init__(*args, **kwargs)

        self.db_url = db_url

    async def on_ready(self):
        await Tortoise.init(db_url=self.db_url, modules={"models": ["models"]})
        await Tortoise.generate_schemas()

        print("ready")
