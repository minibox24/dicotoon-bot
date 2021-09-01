import discord
from discord.ext import commands
from discord.ui.view import View
from discord.ui.button import button


class ConfirmView(View):
    def __init__(self, user_id, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.user_id = user_id
        self.confirm = False

    @button(label="네", style=discord.ButtonStyle.green)
    async def yes(self, _, interaction):
        if interaction.user.id != self.user_id:
            return

        self.confirm = True
        self.stop()

    @button(label="아니오", style=discord.ButtonStyle.red)
    async def no(self, _, interaction):
        if interaction.user.id != self.user_id:
            return

        self.stop()


class DicoToonCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(DicoToonCog(bot))
