from discord.ext.commands import Bot

class DicoToon(Bot):
    def __init__(self, *args, **kwargs):
        if not kwargs.get("command_prefix"):
            kwargs["command_prefix"] = "!"

        super().__init__(*args, **kwargs)

    async def on_ready(self):
        print('ready')
