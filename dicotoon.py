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

    async def get_user(self, user):
        toon_user = await ToonUser.filter(id=user.id).first()

        if not toon_user:
            toon_user = await ToonUser.create(
                id=user.id,
                name=user.name,
                avatar=user.display_avatar.url,
            )

        return toon_user

    async def fetch_all(self, channel: discord.TextChannel):
        stop_count = 0
        toon_channel = await ToonChannel.get(id=channel.id)
        users = {}

        async for message in channel.history(limit=None):
            if not message.attachments:
                stop_count += 1
                continue

            if list(filter(lambda r: r.emoji == "\N{GLOWING STAR}", message.reactions)):
                attachment = message.attachments[0]

                if not attachment.content_type.startswith("image/"):
                    continue

                user = users.get(message.author.id)

                if not user:
                    user = await self.get_user(message.author)
                    users[message.author.id] = user

                await ToonData.create(
                    message_id=message.id,
                    url=attachment.url,
                    user=user,
                    channel=toon_channel,
                    created_at=message.created_at,
                )

                stop_count = 0
            else:
                stop_count += 1

            if stop_count >= 200:
                break

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

        if await ToonChannel.exists(id=channel.id):
            return await ctx.send("이미 등록된 채널이에요.")

        name = discord.utils.escape_markdown(name)

        if not channel.permissions_for(ctx.author).manage_channels:
            return await ctx.send(
                f"{ctx.author.name}님은 {channel.mention}에 채널 관리 권한이 없어요."
            )

        if not channel.permissions_for(ctx.guild.me).read_message_history:
            return await ctx.send(f"{channel.mention}에서 저에게 메시지 기록 보기 권한이 필요해요.")

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

        await self.bot.loop.create_task(self.fetch_all(channel))

    @commands.command("탈퇴")
    async def unregister(self, ctx, channel: discord.TextChannel = None):
        if not channel:
            channel = ctx.channel

        toon_channel = await ToonChannel.filter(id=channel.id).first()

        if not toon_channel:
            return await ctx.send("등록되지 않은 채널이에요.")

        if not channel.permissions_for(ctx.author).manage_channels:
            return await ctx.send(
                f"{ctx.author.name}님은 {channel.mention}에 채널 관리 권한이 없어요."
            )

        view = ConfirmView(ctx.author.id)
        msg = await ctx.reply(f"정말로 {channel.mention}을(를) 디코툰 서비스에서 탈퇴할까요?", view=view)

        await view.wait()

        if not view.confirm:
            return await msg.edit("취소했어요.", embed=None, view=None)

        await toon_channel.delete()

        await msg.edit(f"{channel.mention}을(를) 디코툰 서비스에서 탈퇴했어요.", embed=None, view=None)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.emoji != "\N{GLOWING STAR}":
            return

        toon_channel = await ToonChannel.filter(id=payload.channel_id).first()

        if not toon_channel:
            return

        message = await (self.bot.get_channel(payload.channel_id)).fetch_message(
            payload.message_id
        )

        if not message.attachments or not message.attachments[
            0
        ].content_type.startswith("image/"):
            return

        url = message.attachments[0].url
        if await ToonData.exists(url=url.split("/attachments/")[-1]):
            return

        user = await self.get_user(message.author)

        await ToonData.create(
            url=url,
            user=user,
            channel=toon_channel,
            created_at=message.created_at,
        )

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.emoji != "\N{GLOWING STAR}":
            return

        toon_data = await ToonData.filter(message_id=payload.message_id).first()

        if toon_data:
            message = await (self.bot.get_channel(payload.channel_id)).fetch_message(
                payload.message_id
            )

            if not list(
                filter(lambda r: r.emoji == "\N{GLOWING STAR}", message.reactions)
            ):
                await toon_data.delete()

    @commands.Cog.listener()
    async def on_raw_reaction_clear(self, payload):
        toon_data = await ToonData.filter(message_id=payload.message_id).first()

        if toon_data:
            await toon_data.delete()

    @commands.Cog.listener()
    async def on_raw_reaction_clear_emoji(self, payload):
        if payload.emoji != "\N{GLOWING STAR}":
            return

        toon_data = await ToonData.filter(message_id=payload.message_id).first()

        if toon_data:
            await toon_data.delete()

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        toon_data = await ToonData.filter(message_id=payload.message_id).first()

        if toon_data:
            await toon_data.delete()

    @commands.Cog.listener()
    async def on_raw_bulk_message_delete(self, payload):
        for i in payload.message_ids:
            toon_data = await ToonData.filter(message_id=i).first()

            if toon_data:
                await toon_data.delete()


def setup(bot):
    bot.add_cog(DicoToonCog(bot))
