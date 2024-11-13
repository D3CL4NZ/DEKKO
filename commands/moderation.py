import discord
from discord import app_commands
from discord.ext import commands
from discord.utils import get

import config

import time

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='kick', with_app_command=True)
    @app_commands.allowed_installs(guilds=True, users=False)
    @app_commands.allowed_contexts(guilds=True, dms=False, private_channels=True)
    @commands.has_any_role("supreme leader", "administrator", "moderator", "Supreme Leader", "Administrator", "Moderator")
    async def _kick(self, ctx, *, user: discord.User, reason: str=None):
        """Kicks a user"""

        async with ctx.typing():
            response = await ctx.send(":hourglass:  **Please wait...**")
            log_channel = self.bot.get_channel(config.LOG_CHANNEL_ID)

            if user.id == self.bot.user.id:
                await response.edit(content="Bite me.")
                return

            if user not in ctx.guild.members:
                await response.edit(content=f":warning:  **{user.mention} is not on this server.**")
                return

            embed = discord.Embed(description=f"{user.mention} **has been kicked.**", color=discord.Colour.red())

            log_embed = discord.Embed(
                title=None,
                description=f":boot: :dash: {user.mention} **was kicked**",
                color=discord.Colour.red()
            )
            log_embed.set_author(name=user.name, icon_url=user.display_avatar.url)
            log_embed.set_thumbnail(url=user.display_avatar.url)
            log_embed.add_field(name="Reason", value=f"{reason if reason else 'No reason provided'}", inline=False)
            log_embed.timestamp = discord.utils.utcnow()
            log_embed.set_footer(text=f"User ID: {user.id}")

            try:
                if reason:
                    await user.send(f"""You have been kicked from `{ctx.guild.name}`.

**Kicked by:** {ctx.author.mention}
**Reason:** `{reason}`

-# **Notice:** I am a bot. This message was sent automatically. Please do not respond to this message.""")
                else:
                    await user.send(f"""You have been kicked from `{ctx.guild.name}`.

**Kicked by:** {ctx.author.mention}
**Reason:** `No reason provided`

-# **Notice:** I am a bot. This message was sent automatically. Please do not respond to this message.""")
            except:
                pass

            await ctx.guild.kick(user, reason=reason)
            await response.edit(content=None, embed=embed)
            await log_channel.send(embed=log_embed)

    @_kick.error
    async def _kick_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send(""":no_entry:  **ACCESS DENIED CYKA**```java
Exception in thread "main" java.lang.SecurityException: Permission Denial
\tat me.declanz.DEKKO(bot.java:249)
\tat me.declanz.DEKKO.PermissionCheck(events.java:12)
\tat me.declanz.DEKKO.moderation(moderation.java:33)
```""")
            await self.bot.get_channel(config.ERROR_CHANNEL_ID).send(""":no_entry:  **AN ERROR HAS OCCURED**```java
Exception in thread "main" java.lang.SecurityException: Permission Denial
\tat me.declanz.DEKKO(bot.java:249)
\tat me.declanz.DEKKO.PermissionCheck(events.java:12)
\tat me.declanz.DEKKO.moderation(moderation.java:33)
```""")

    @commands.hybrid_command(name='ban', with_app_command=True)
    @app_commands.allowed_installs(guilds=True, users=False)
    @app_commands.allowed_contexts(guilds=True, dms=False, private_channels=True)
    @commands.has_any_role("supreme leader", "administrator", "moderator", "Supreme Leader", "Administrator", "Moderator")
    async def _ban(self, ctx, *, user: discord.User, reason: str=None):
        """Bans a user"""

        async with ctx.typing():
            response = await ctx.send(":hourglass:  **Please wait...**")
            log_channel = self.bot.get_channel(config.LOG_CHANNEL_ID)

            if user.id == self.bot.user.id:
                await response.edit(content="Bite me.")
                return

            embed = discord.Embed(description=f"{user.mention} **has been banned.**", color=discord.Colour.red())

            log_embed = discord.Embed(
                title=None,
                description=None,
                color=discord.Colour.red()
            )
            log_embed.set_author(name=f"[BAN] {user.name}", icon_url=user.display_avatar.url)
            log_embed.add_field(name="User", value=user.mention, inline=True)
            log_embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            log_embed.add_field(name="Reason", value=f"{reason if reason else 'Unspecified'}", inline=True)

            try:
                if reason:
                    await user.send(f"""You have been <a:banned1:1267853070432337940><a:banned2:1267853071661138001><a:banned3:1267853072294613006> from `{ctx.guild.name}`.

**Banned by:** {ctx.author.mention}
**Reason:** `{reason}`

-# **Notice:** I am a bot. This message was sent automatically. Please do not respond to this message.""")
                else:
                    await user.send(f"""You have been <a:banned1:1267853070432337940><a:banned2:1267853071661138001><a:banned3:1267853072294613006> from `{ctx.guild.name}`.

**Banned by:** {ctx.author.mention}
**Reason:** `No reason provided`

-# **Notice:** I am a bot. This message was sent automatically. Please do not respond to this message.""")
            except:
                pass

            await ctx.guild.ban(user, reason=reason)

            await response.edit(content=None, embed=embed)
            await log_channel.send(embed=log_embed)

    @_ban.error
    async def _ban_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send(""":no_entry:  **ACCESS DENIED CYKA**```java
Exception in thread "main" java.lang.SecurityException: Permission Denial
\tat me.declanz.DEKKO(bot.java:249)
\tat me.declanz.DEKKO.PermissionCheck(events.java:12)
\tat me.declanz.DEKKO.moderation(moderation.java:33)
```""")

            await self.bot.get_channel(config.ERROR_CHANNEL_ID).send(""":no_entry:  **AN ERROR HAS OCCURED**```java
Exception in thread "main" java.lang.SecurityException: Permission Denial
\tat me.declanz.DEKKO(bot.java:249)
\tat me.declanz.DEKKO.PermissionCheck(events.java:12)
\tat me.declanz.DEKKO.moderation(moderation.java:33)
```""")

    @commands.hybrid_command(name='pardon', with_app_command=True)
    @app_commands.allowed_installs(guilds=True, users=False)
    @app_commands.allowed_contexts(guilds=True, dms=False, private_channels=True)
    @commands.has_any_role("supreme leader", "administrator", "moderator", "Supreme Leader", "Administrator", "Moderator")
    async def _pardon(self, ctx, *, user: discord.User):
        """Unbans a user"""

        async with ctx.typing():
            response = await ctx.send(":hourglass:  **Please wait...**")
            log_channel = self.bot.get_channel(config.LOG_CHANNEL_ID)

            if user.id == self.bot.user.id:
                await response.edit(content="Bite me.")
                return

            try:
                await ctx.guild.fetch_ban(user)
            except:
                await response.edit(content=None, embed=discord.Embed(description=f"{user.mention} **is not currently banned.**", color=discord.Colour.yellow()))
                return

            embed = discord.Embed(description=f"{user.mention} **has been unbanned.**", color=discord.Colour.green())

            log_embed = discord.Embed(
                title=None,
                description=None,
                color=discord.Colour.green()
            )
            log_embed.set_author(name=f"[UNBAN] {user.name}", icon_url=user.display_avatar.url)
            log_embed.add_field(name="User", value=user.mention, inline=True)
            log_embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)

            await ctx.guild.unban(user)

            await log_channel.send(embed=log_embed)

            try:
                await user.send(f"""You have been unbanned from `{ctx.guild.name}`.
Here is the link to join again: https://discord.gg/8JnExCu76H

-# **Notice:** I am a bot. This message was sent automatically. Please do not respond to this message.""")
            except:
                await response.edit(content=f"Warning: {user.mention} has their DMs closed. Make sure you let them know that they were unbanned.", embed=embed)
            else:
                await response.edit(content=None, embed=embed)

    @_pardon.error
    async def _pardon_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send(""":no_entry:  **ACCESS DENIED CYKA**```java
Exception in thread "main" java.lang.SecurityException: Permission Denial
\tat me.declanz.DEKKO(bot.java:249)
\tat me.declanz.DEKKO.PermissionCheck(events.java:12)
\tat me.declanz.DEKKO.moderation(moderation.java:33)
```""")

            await self.bot.get_channel(config.ERROR_CHANNEL_ID).send(""":no_entry:  **AN ERROR HAS OCCURED**```java
Exception in thread "main" java.lang.SecurityException: Permission Denial
\tat me.declanz.DEKKO(bot.java:249)
\tat me.declanz.DEKKO.PermissionCheck(events.java:12)
\tat me.declanz.DEKKO.moderation(moderation.java:33)
```""")

async def setup(bot):
    await bot.add_cog(Moderation(bot))
