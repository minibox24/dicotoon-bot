from discord import Activity, ActivityType
from discord.ext.commands import Bot
from tortoise import Tortoise


class DicoToon(Bot):
    def __init__(self, db_url, *args, **kwargs):
        if not kwargs.get("command_prefix"):
            kwargs["command_prefix"] = "dt!"

        super().__init__(*args, **kwargs)

        self.remove_command("help")

        self.db_url = db_url

    async def on_ready(self):
        await Tortoise.init(db_url=self.db_url, modules={"models": ["models"]})
        await Tortoise.generate_schemas()

        self.load_extension("jishaku")
        self.load_extension("dicotoon")

        await self.change_presence(
            activity=Activity(
                type=ActivityType.watching,
                name=f"dt!도움",
            )
        )

        print("ready")
