import discord
from discord import app_commands
from discord.ext import commands
from discord.utils import get

import config

import time

class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='verify', with_app_command=True)
    @app_commands.allowed_installs(guilds=True, users=False)
    @app_commands.allowed_contexts(guilds=True, dms=False, private_channels=True)
    @commands.has_any_role("supreme leader", "administrator", "moderator", "Supreme Leader", "Administrator", "Moderator")
    async def _verify(self, ctx, *, member: discord.Member):
        """Verifies a user"""

        verified_role = discord.utils.get(member.guild.roles, name='Citizen')
        human_role = discord.utils.get(member.guild.roles, name='human')
        log_channel = self.bot.get_channel(config.LOG_CHANNEL_ID)

        if member.id == self.bot.user.id:
            await ctx.send("Bite me.")
            return

        if verified_role in member.roles:
            await ctx.send(f":warning:  {member.mention} **IS ALREADY VERIFIED**")
            return

        embed = discord.Embed(description=f"{member.mention} **is now verified.**", color=discord.Colour.green())

        try:
            await member.send(f"""You are now verified on `{ctx.guild.name}`. Please remember to obey the rules and have fun!

-# **Notice:** I am a bot. This message was sent automatically. Please do not respond to this message.""")
        except:
            await ctx.send(f"Warning: {user.mention} has their DMs closed. Make sure you let them know that they are now verified.", embed=embed)
        else:
            await ctx.send(embed=embed)

        await member.edit(roles=[human_role, verified_role])

        log_embed = discord.Embed(
            title=None,
            description=f":white_check_mark: {member.mention} **was verified**",
            color=discord.Colour.green()
        )
        log_embed.set_author(name=member.name, icon_url=member.display_avatar.url)
        log_embed.set_thumbnail(url=member.display_avatar.url)
        log_embed.timestamp = discord.utils.utcnow()
        log_embed.set_footer(text=f"User ID: {member.id}")

        await log_channel.send(embed=log_embed)

    @_verify.error
    async def _verify_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send(""":no_entry:  **ACCESS DENIED CYKA**```java
Exception in thread "main" java.lang.SecurityException: Permission Denial
\tat me.declanz.DEKKO(bot.java:249)
\tat me.declanz.DEKKO.PermissionCheck(events.java:12)
\tat me.declanz.DEKKO.verification(verification.java:33)
```""")
            await self.bot.get_channel(config.ERROR_CHANNEL_ID).send(""":no_entry:  **AN ERROR HAS OCCURED**```java
Exception in thread "main" java.lang.SecurityException: Permission Denial
\tat me.declanz.DEKKO(bot.java:249)
\tat me.declanz.DEKKO.PermissionCheck(events.java:12)
\tat me.declanz.DEKKO.verification(verification.java:33)
```""")

    @commands.hybrid_command(name='unverify', with_app_command=True)
    @app_commands.allowed_installs(guilds=True, users=False)
    @app_commands.allowed_contexts(guilds=True, dms=False, private_channels=True)
    @commands.has_any_role("supreme leader", "administrator", "moderator", "Supreme Leader", "Administrator", "Moderator")
    async def _unverify(self, ctx, *, member: discord.Member):
        """Unverifies a user"""

        purgatory_role = discord.utils.get(member.guild.roles, name='purgatory')
        log_channel = self.bot.get_channel(config.LOG_CHANNEL_ID)

        if member.id == self.bot.user.id:
            await ctx.send("Bite me.")
            return

        if purgatory_role in member.roles:
            await ctx.send(f":warning:  {member.mention} **IS ALREADY IN PURGATORY**")
            return

        await member.edit(roles=[purgatory_role])
        embed = discord.Embed(description=f"{member.mention} **is no longer verified.**", color=discord.Colour.red())

        log_embed = discord.Embed(
            title=None,
            description=f":prohibited: {member.mention} **was unverified**",
            color=discord.Colour.red()
        )
        log_embed.set_author(name=member.name, icon_url=member.display_avatar.url)
        log_embed.set_thumbnail(url=member.display_avatar.url)
        log_embed.timestamp = discord.utils.utcnow()
        log_embed.set_footer(text=f"User ID: {member.id}")

        await ctx.send(embed=embed)
        await log_channel.send(embed=log_embed)

    @_unverify.error
    async def _unverify_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send(""":no_entry:  **ACCESS DENIED CYKA**```java
Exception in thread "main" java.lang.SecurityException: Permission Denial
\tat me.declanz.DEKKO(bot.java:249)
\tat me.declanz.DEKKO.PermissionCheck(events.java:12)
\tat me.declanz.DEKKO.verification(verification.java:33)
```""")

            await self.bot.get_channel(config.ERROR_CHANNEL_ID).send(""":no_entry:  **AN ERROR HAS OCCURED**```java
Exception in thread "main" java.lang.SecurityException: Permission Denial
\tat me.declanz.DEKKO(bot.java:249)
\tat me.declanz.DEKKO.PermissionCheck(events.java:12)
\tat me.declanz.DEKKO.verification(verification.java:33)
```""")

async def setup(bot):
    await bot.add_cog(Verification(bot))
