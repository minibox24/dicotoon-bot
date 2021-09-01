import discord
from discord.ext import commands
from discord.ui.view import View
from discord.ui.button import button

from tortoise import Tortoise
from models import *


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

    @commands.command("종료")
    @commands.is_owner()
    async def exit_bot(self, ctx):
        await ctx.send("봇을 종료할게요.")
        await Tortoise.close_connections()
        await self.bot.close()

    @commands.command("등록")
    async def register(self, ctx, name, channel: discord.TextChannel = None):
        if not channel:
            channel = ctx.channel

        if ToonChannel.exists(id=channel.id):
            return await ctx.send("이미 등록된 채널이에요.")

        name = discord.utils.escape_markdown(name)

        if not ctx.channel.permissions_for(ctx.author).manage_channels:
            return await ctx.send(
                f"{ctx.author.name}님은 {channel.mention}에 채널 관리 권한이 없어요."
            )

        embed = discord.Embed(
            title="확인",
            description=f"채널 {channel.mention}을(를) `{name}`(이)라는 이름으로 디코툰 서비스에 등록할까요?",
            color=discord.Color.yellow(),
        )
        embed.add_field(
            name="주의 사항",
            value="\n".join(
                [
                    "1. 채널을 디코툰 서비스에 등록하게 된다면 채널 아이디를 알고 있는 모든 사람들이 채널의 사진들을 확인할 수 있게 됩니다.",
                    "2. 등록한 채널에서 :star2: 리액션이 달리게 된 모든 사진들의 URL은 서비스 탈퇴시까지 데이터베이스에 남아있게 됩니다.",
                    "3. 데이터베이스에 남아있는 사진들은 관리자가 비밀로 확인할 수 있고, Discord TOS에 위반하는 사진이 있다면 즉시 블랙리스트 처리됩니다.",
                ]
            ),
        )
        embed.set_footer(text="꼭 주의 사항을 읽고 선택해주세요.")

        view = ConfirmView(ctx.author.id)
        msg = await ctx.reply(embed=embed, view=view)

        await view.wait()

        if not view.confirm:
            return await msg.edit("취소했어요.", embed=None, view=None)

        await ToonChannel.create(id=channel.id, name=name)

        await msg.edit("채널을 디코툰 서비스에 등록했어요.", embed=None, view=None)


def setup(bot):
    bot.add_cog(DicoToonCog(bot))
