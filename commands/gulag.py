import discord
from discord import app_commands
from discord.ext import commands

from database import db

class Gulag(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='gulag', with_app_command=True)
    @app_commands.allowed_installs(guilds=True, users=False)
    @app_commands.allowed_contexts(guilds=True, dms=False, private_channels=True)
    @commands.has_permissions(moderate_members=True)
    async def _gulag(self, ctx, *, member: discord.Member):
        """Sends the user to GULAG"""

        gulag_role = member.guild.get_role(await db.fetch_one("SELECT mute_role_id FROM config WHERE guild = ?", member.guild.id))
        log_channel = self.bot.get_channel(await db.fetch_one("SELECT log_channel FROM config WHERE guild = ?", member.guild.id))

        if gulag_role is None:
            return await ctx.send(":warning:  **GULAG IS NOT SET UP**")

        if member.id == self.bot.user.id:
            await ctx.send("Bite me.")
            return

        if gulag_role in member.roles:
            await ctx.send(f":warning:  **{member.mention} IS ALREADY IN GULAG**")
            return

        await member.add_roles(gulag_role)

        embed = discord.Embed(
            title=None,
            description=f"{member.mention} **was sent to {gulag_role.mention}!**",
            color=discord.Colour.gold()
        )
        embed.set_image(url="attachment://gulag.gif")

        await ctx.send(file=discord.File("./img/gulag.gif", filename="gulag.gif"), embed=embed)

        try:
            await member.send(f"""You have been muted in `{ctx.guild.name}`.

**Muted by:** {ctx.author.mention}

-# **Notice:** I am a bot. This message was sent automatically. Please do not respond to this message.""")
        except:
            pass

        if log_channel:
            log_embed = discord.Embed(
                title=None,
                description=f":lock: {member.mention} **was sent to gulag**",
                color=discord.Colour.gold()
            )
            log_embed.set_author(name=member.name, icon_url=member.display_avatar.url)
            log_embed.set_thumbnail(url=member.display_avatar.url)
            log_embed.timestamp = discord.utils.utcnow()
            log_embed.set_footer(text=f"User ID: {member.id}")

            await log_channel.send(embed=log_embed)

    @_gulag.error
    async def _gulag_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send(""":no_entry:  **ACCESS DENIED CYKA**```java
Exception in thread "main" java.lang.SecurityException: Permission Denial
\tat me.declanz.DEKKO(bot.java:249)
\tat me.declanz.DEKKO.PermissionCheck(events.java:12)
\tat me.declanz.DEKKO.gulag(gulag.java:33)
```""")
            await self.bot.get_channel(await db.fetch_one("SELECT error_channel FROM config WHERE guild = ?", ctx.guild.id)).send(""":no_entry:  **AN ERROR HAS OCCURED**```java
Exception in thread "main" java.lang.SecurityException: Permission Denial
\tat me.declanz.DEKKO(bot.java:249)
\tat me.declanz.DEKKO.PermissionCheck(events.java:12)
\tat me.declanz.DEKKO.gulag(gulag.java:33)
```""")

    @commands.hybrid_command(name='release', with_app_command=True)
    @app_commands.allowed_installs(guilds=True, users=False)
    @app_commands.allowed_contexts(guilds=True, dms=False, private_channels=True)
    @commands.has_permissions(moderate_members=True)
    async def _release(self, ctx, *, member: discord.Member):
        """Releases the user from GULAG"""

        gulag_role = member.guild.get_role(await db.fetch_one("SELECT mute_role_id FROM config WHERE guild = ?", member.guild.id))
        log_channel = self.bot.get_channel(await db.fetch_one("SELECT log_channel FROM config WHERE guild = ?", member.guild.id))

        if gulag_role is None:
            return await ctx.send(":warning:  **GULAG IS NOT SET UP**")

        if member.id == self.bot.user.id:
            await ctx.send("Bite me.")
            return

        if gulag_role not in member.roles:
            await ctx.send(f":warning:  **{member.mention} IS NOT CURRENTLY IN GULAG**")
            return

        await member.remove_roles(gulag_role)
        embed = discord.Embed(description=f"{member.mention} **was released from {gulag_role.mention}**", color=discord.Colour.gold())

        await ctx.send(embed=embed)

        if log_channel:
            log_embed = discord.Embed(
                title=None,
                description=f":unlock: {member.mention} **was released from gulag**",
                color=discord.Colour.gold()
            )
            log_embed.set_author(name=member.name, icon_url=member.display_avatar.url)
            log_embed.set_thumbnail(url=member.display_avatar.url)
            log_embed.timestamp = discord.utils.utcnow()
            log_embed.set_footer(text=f"User ID: {member.id}")

            await log_channel.send(embed=log_embed)

    @_release.error
    async def _release_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send(""":no_entry:  **ACCESS DENIED CYKA**```java
Exception in thread "main" java.lang.SecurityException: Permission Denial
\tat me.declanz.DEKKO(bot.java:249)
\tat me.declanz.DEKKO.PermissionCheck(events.java:12)
\tat me.declanz.DEKKO.gulag(gulag.java:33)
```""")

            await self.bot.get_channel(await db.fetch_one("SELECT error_channel FROM config WHERE guild = ?", ctx.guild.id)).send(""":no_entry:  **AN ERROR HAS OCCURED**```java
Exception in thread "main" java.lang.SecurityException: Permission Denial
\tat me.declanz.DEKKO(bot.java:249)
\tat me.declanz.DEKKO.PermissionCheck(events.java:12)
\tat me.declanz.DEKKO.gulag(gulag.java:33)
```""")

async def setup(bot):
    await bot.add_cog(Gulag(bot))
