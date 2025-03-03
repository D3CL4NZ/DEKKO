import discord
from discord import app_commands
from discord.ext import commands

from webhook import DiscordWebhookSender

from database import db

class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='verify', with_app_command=True)
    @app_commands.allowed_installs(guilds=True, users=False)
    @app_commands.allowed_contexts(guilds=True, dms=False, private_channels=True)
    @commands.has_permissions(moderate_members=True)
    async def _verify(self, ctx, *, member: discord.Member):
        """Verifies a user"""

        verified_role_id = await db.fetch_one("SELECT verified_role_id FROM config WHERE guild = ?", ctx.guild.id)
        verified_role = member.guild.get_role(verified_role_id[0]) if verified_role_id else None

        human_role_id = await db.fetch_one("SELECT human_role_id FROM config WHERE guild = ?", ctx.guild.id)
        human_role = member.guild.get_role(human_role_id[0]) if human_role_id else None

        log_webhook_url = await db.fetch_one("SELECT log_webhook FROM logging_webhooks WHERE guild = ?", ctx.guild.id)
        log_webhook = DiscordWebhookSender(url=log_webhook_url[0]) if not(log_webhook_url is None or (isinstance(log_webhook_url, tuple) and all(url is None for url in log_webhook_url))) else None

        if verified_role is None or human_role is None:
            return await ctx.send(":warning:  **VERIFICATION IS NOT SET UP**")

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
            await ctx.send(f"Warning: {member.mention} has their DMs closed. Make sure you let them know that they are now verified.", embed=embed)
        else:
            await ctx.send(embed=embed)

        await member.edit(roles=[human_role, verified_role])

        if log_webhook:
            log_embed = discord.Embed(
                title=None,
                description=f":white_check_mark: {member.mention} **was verified**",
                color=discord.Colour.green()
            )
            log_embed.set_author(name=member.name, icon_url=member.display_avatar.url)
            log_embed.set_thumbnail(url=member.display_avatar.url)
            log_embed.timestamp = discord.utils.utcnow()
            log_embed.set_footer(text=f"User ID: {member.id}")

            await log_webhook.send(embed=log_embed)

    @_verify.error
    async def _verify_error(self, ctx, error):
        error_webhook_url = await db.fetch_one("SELECT error_webhook FROM logging_webhooks WHERE guild = ?", ctx.guild.id)
        error_webhook = DiscordWebhookSender(url=error_webhook_url[0]) if not(error_webhook_url is None or (isinstance(error_webhook_url, tuple) and all(url is None for url in error_webhook_url))) else None

        if isinstance(error, commands.CheckFailure):
            await ctx.send(""":no_entry:  **ACCESS DENIED CYKA**```java
Exception in thread "main" java.lang.SecurityException: Permission Denial
\tat me.declanz.DEKKO(bot.java:249)
\tat me.declanz.DEKKO.PermissionCheck(events.java:12)
\tat me.declanz.DEKKO.verification(verification.java:33)
```""")
            if error_webhook:
                await error_webhook.send(""":no_entry:  **AN ERROR HAS OCCURED**```java
Exception in thread "main" java.lang.SecurityException: Permission Denial
\tat me.declanz.DEKKO(bot.java:249)
\tat me.declanz.DEKKO.PermissionCheck(events.java:12)
\tat me.declanz.DEKKO.verification(verification.java:33)
```""")

    @commands.hybrid_command(name='unverify', with_app_command=True)
    @app_commands.allowed_installs(guilds=True, users=False)
    @app_commands.allowed_contexts(guilds=True, dms=False, private_channels=True)
    @commands.has_permissions(moderate_members=True)
    async def _unverify(self, ctx, *, member: discord.Member):
        """Unverifies a user"""

        purgatory_role_id = await db.fetch_one("SELECT purgatory_role_id FROM config WHERE guild = ?", ctx.guild.id)
        purgatory_role = member.guild.get_role(purgatory_role_id[0]) if purgatory_role_id else None

        log_webhook_url = await db.fetch_one("SELECT log_webhook FROM logging_webhooks WHERE guild = ?", ctx.guild.id)
        log_webhook = DiscordWebhookSender(url=log_webhook_url[0]) if not(log_webhook_url is None or (isinstance(log_webhook_url, tuple) and all(url is None for url in log_webhook_url))) else None

        if purgatory_role is None:
            return await ctx.send(":warning:  **PURGATORY IS NOT SET UP**")

        if member.id == self.bot.user.id:
            await ctx.send("Bite me.")
            return

        if purgatory_role in member.roles:
            await ctx.send(f":warning:  {member.mention} **IS ALREADY IN PURGATORY**")
            return

        await member.edit(roles=[purgatory_role])
        embed = discord.Embed(description=f"{member.mention} **is no longer verified.**", color=discord.Colour.red())

        await ctx.send(embed=embed)

        if log_webhook:
            log_embed = discord.Embed(
                title=None,
                description=f":prohibited: {member.mention} **was unverified**",
                color=discord.Colour.red()
            )
            log_embed.set_author(name=member.name, icon_url=member.display_avatar.url)
            log_embed.set_thumbnail(url=member.display_avatar.url)
            log_embed.timestamp = discord.utils.utcnow()
            log_embed.set_footer(text=f"User ID: {member.id}")

            await log_webhook.send(embed=log_embed)

    @_unverify.error
    async def _unverify_error(self, ctx, error):
        error_webhook_url = await db.fetch_one("SELECT error_webhook FROM logging_webhooks WHERE guild = ?", ctx.guild.id)
        error_webhook = DiscordWebhookSender(url=error_webhook_url[0]) if not(error_webhook_url is None or (isinstance(error_webhook_url, tuple) and all(url is None for url in error_webhook_url))) else None

        if isinstance(error, commands.CheckFailure):
            await ctx.send(""":no_entry:  **ACCESS DENIED CYKA**```java
Exception in thread "main" java.lang.SecurityException: Permission Denial
\tat me.declanz.DEKKO(bot.java:249)
\tat me.declanz.DEKKO.PermissionCheck(events.java:12)
\tat me.declanz.DEKKO.verification(verification.java:33)
```""")
            if error_webhook:
                await error_webhook.send(""":no_entry:  **AN ERROR HAS OCCURED**```java
Exception in thread "main" java.lang.SecurityException: Permission Denial
\tat me.declanz.DEKKO(bot.java:249)
\tat me.declanz.DEKKO.PermissionCheck(events.java:12)
\tat me.declanz.DEKKO.verification(verification.java:33)
```""")

async def setup(bot):
    await bot.add_cog(Verification(bot))
