import discord
from discord import app_commands
from discord.ext import commands

import time

from database import db

class Setup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_group(name="setup", invoke_without_command=True)
    @app_commands.allowed_installs(guilds=True, users=False)
    @app_commands.allowed_contexts(guilds=True, dms=False, private_channels=True)
    async def _setup(self, ctx):
        await ctx.send(':warning:  **You must specify a subcommand**')

    @_setup.command(name='global', invoke_without_subcommand=True, with_app_command=True)
    @app_commands.allowed_installs(guilds=True, users=False)
    @app_commands.allowed_contexts(guilds=True, dms=False, private_channels=True)
    @commands.is_owner()
    async def _setup_global(self, ctx, *, option: str, value: str):
        """Edits a global configuration option"""

        async with ctx.typing():
            response = await ctx.send(":hourglass:  **Please wait...**")

            if option.lower() == "dm_channel":
                await response.edit(content=f""":gear:  **DEKKO is executing an SQL query...**
Query: `UPDATE global_config SET dm_channel = {value}`
Requested by: `DEKKO Command Processor`
Started: <t:{int(time.time())}:R>""")
                await db.execute("UPDATE global_config SET dm_channel = ?", value)
                await response.edit(content=f":white_check_mark:  **DM CHANNEL SET TO <#{value}>**")
            else:
                await response.edit(content=":warning:  **INVALID OPTION**")

    @_setup_global.error
    async def _edit_global_config_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send(""":no_entry:  **ACCESS DENIED CYKA**```java
Exception in thread "main" java.lang.SecurityException: Permission Denial
\tat me.declanz.DEKKO(bot.java:249)
\tat me.declanz.DEKKO.PermissionCheck(events.java:12)
\tat me.declanz.DEKKO.setup(setup.java:37)
```""")

            await self.bot.get_channel(await db.fetch_one("SELECT error_channel FROM config WHERE guild = ?", ctx.guild.id)).send(""":no_entry:  **AN ERROR HAS OCCURED**```java
Exception in thread "main" java.lang.SecurityException: Permission Denial
\tat me.declanz.DEKKO(bot.java:249)
\tat me.declanz.DEKKO.PermissionCheck(events.java:12)
\tat me.declanz.DEKKO.setup(setup.java:37)
```""")

    @_setup.command(name='channels', invoke_without_subcommand=True, with_app_command=True)
    @app_commands.allowed_installs(guilds=True, users=False)
    @app_commands.allowed_contexts(guilds=True, dms=False, private_channels=True)
    @commands.has_permissions(administrator=True)
    async def _setup_channels(self, ctx, *, option: str, channel: discord.abc.GuildChannel):
        """Edits a channel configuration option"""

        async with ctx.typing():
            response = await ctx.send(":hourglass:  **Please wait...**")

            if option.lower() == "log_channel":
                await response.edit(content=f""":gear:  **DEKKO is executing an SQL query...**
Query: `UPDATE config SET log_channel = {channel.id} WHERE guild = {ctx.guild.id}`
Requested by: `DEKKO Command Processor`
Started: <t:{int(time.time())}:R>""")
                await db.execute("UPDATE config SET log_channel = ? WHERE guild = ?", channel.id, ctx.guild.id)
                await response.edit(content=f":white_check_mark:  **LOG CHANNEL SET TO {channel.mention}**")
            elif option.lower() == "error_channel":
                await response.edit(content=f""":gear:  **DEKKO is executing an SQL query...**
Query: `UPDATE config SET error_channel = {channel.id} WHERE guild = {ctx.guild.id}`
Requested by: `DEKKO Command Processor`
Started: <t:{int(time.time())}:R>""")
                await db.execute("UPDATE config SET error_channel = ? WHERE guild = ?", channel.id, ctx.guild.id)
                await response.edit(content=f":white_check_mark:  **ERROR CHANNEL SET TO {channel.mention}**")
            elif option.lower() == "admin_channel":
                await response.edit(content=f""":gear:  **DEKKO is executing an SQL query...**
Query: `UPDATE config SET admin_channel = {channel.id} WHERE guild = {ctx.guild.id}`
Requested by: `DEKKO Command Processor`
Started: <t:{int(time.time())}:R>""")
                await db.execute("UPDATE config SET admin_channel = ? WHERE guild = ?", channel.id, ctx.guild.id)
                await response.edit(content=f":white_check_mark:  **ADMIN CHANNEL SET TO {channel.mention}**")
            elif option.lower() == "verification_channel":
                await response.edit(content=f""":gear:  **DEKKO is executing an SQL query...**
Query: `UPDATE config SET manver_channel = {channel.id} WHERE guild = {ctx.guild.id}`
Requested by: `DEKKO Command Processor`
Started: <t:{int(time.time())}:R>""")
                await db.execute("UPDATE config SET manver_channel = ? WHERE guild = ?", channel.id, ctx.guild.id)
                await response.edit(content=f":white_check_mark:  **VERIFICATION CHANNEL SET TO {channel.mention}**")
            else:
                await response.edit(content=":warning:  **INVALID OPTION**")

    @_setup_channels.error
    async def _edit_channel_config_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send(""":no_entry:  **ACCESS DENIED CYKA**```java
Exception in thread "main" java.lang.SecurityException: Permission Denial
\tat me.declanz.DEKKO(bot.java:249)
\tat me.declanz.DEKKO.PermissionCheck(events.java:12)
\tat me.declanz.DEKKO.setup(setup.java:13)
```""")

            await self.bot.get_channel(await db.fetch_one("SELECT error_channel FROM config WHERE guild = ?", ctx.guild.id)).send(""":no_entry:  **AN ERROR HAS OCCURED**```java
Exception in thread "main" java.lang.SecurityException: Permission Denial
\tat me.declanz.DEKKO(bot.java:249)
\tat me.declanz.DEKKO.PermissionCheck(events.java:12)
\tat me.declanz.DEKKO.setup(setup.java:13)
```""")
            
    @_setup.command(name='exclude-channels', invoke_without_subcommand=True, with_app_command=True)
    @app_commands.allowed_installs(guilds=True, users=False)
    @app_commands.allowed_contexts(guilds=True, dms=False, private_channels=True)
    @commands.has_permissions(administrator=True)
    async def _setup_exclude_channels(self, ctx, *, comma_separated_list_of_channel_ids: str):
        """Excludes a list of channels from logging"""

        async with ctx.typing():
            response = await ctx.send(":hourglass:  **Please wait...**")

            channels = comma_separated_list_of_channel_ids.strip().replace(" ", "")

            await response.edit(content=f""":gear:  **DEKKO is executing an SQL query...**
Query: `UPDATE config SET exclude_logging_channels = "{channels}" WHERE guild = {ctx.guild.id}`
Requested by: `DEKKO Command Processor`
Started: <t:{int(time.time())}:R>""")
            await db.execute("UPDATE config SET exclude_logging_channels = ? WHERE guild = ?", channels, ctx.guild.id)
            await response.edit(content=f":white_check_mark:  **EXCLUDED CHANNELS UPDATED**")

    @_setup_exclude_channels.error
    async def _exclude_logging_channels(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send(""":no_entry:  **ACCESS DENIED CYKA**```java
Exception in thread "main" java.lang.SecurityException: Permission Denial
\tat me.declanz.DEKKO(bot.java:249)
\tat me.declanz.DEKKO.PermissionCheck(events.java:12)
\tat me.declanz.DEKKO.setup(setup.java:42)
```""")

            await self.bot.get_channel(await db.fetch_one("SELECT error_channel FROM config WHERE guild = ?", ctx.guild.id)).send(""":no_entry:  **AN ERROR HAS OCCURED**```java
Exception in thread "main" java.lang.SecurityException: Permission Denial
\tat me.declanz.DEKKO(bot.java:249)
\tat me.declanz.DEKKO.PermissionCheck(events.java:12)
\tat me.declanz.DEKKO.setup(setup.java:42)
```""")

    @_setup.command(name='roles', invoke_without_subcommand=True, with_app_command=True)
    @app_commands.allowed_installs(guilds=True, users=False)
    @app_commands.allowed_contexts(guilds=True, dms=False, private_channels=True)
    @commands.has_permissions(administrator=True)
    async def _setup_roles(self, ctx, *, option: str, role: discord.Role):
        """Edits a role configuration option"""

        async with ctx.typing():
            response = await ctx.send(":hourglass:  **Please wait...**")

            if option.lower() == "owner_role":
                await response.edit(content=f""":gear:  **DEKKO is executing an SQL query...**
Query: `UPDATE config SET owner_role_id = {role.id} WHERE guild = {ctx.guild.id}`
Requested by: `DEKKO Command Processor`
Started: <t:{int(time.time())}:R>""")
                await db.execute("UPDATE config SET owner_role_id = ? WHERE guild = ?", role.id, ctx.guild.id)
                await response.edit(content=f":white_check_mark:  **OWNER ROLE SET TO {role.mention}**")
            elif option.lower() == "admin_role":
                await response.edit(content=f""":gear:  **DEKKO is executing an SQL query...**
Query: `UPDATE config SET admin_role_id = {role.id} WHERE guild = {ctx.guild.id}`
Requested by: `DEKKO Command Processor`
Started: <t:{int(time.time())}:R>""")
                await db.execute("UPDATE config SET admin_role_id = ? WHERE guild = ?", role.id, ctx.guild.id)
                await response.edit(content=f":white_check_mark:  **ADMIN ROLE SET TO {role.mention}**")
            elif option.lower() == "moderator_role":
                await response.edit(content=f""":gear:  **DEKKO is executing an SQL query...**
Query: `UPDATE config SET mod_role_id = {role.id} WHERE guild = {ctx.guild.id}`
Requested by: `DEKKO Command Processor`
Started: <t:{int(time.time())}:R>""")
                await db.execute("UPDATE config SET mod_role_id = ? WHERE guild = ?", role.id, ctx.guild.id)
                await response.edit(content=f":white_check_mark:  **MODERATOR ROLE SET TO {role.mention}**")
            elif option.lower() == "bot_role":
                await response.edit(content=f""":gear:  **DEKKO is executing an SQL query...**
Query: `UPDATE config SET bot_role_id = {role.id} WHERE guild = {ctx.guild.id}`
Requested by: `DEKKO Command Processor`
Started: <t:{int(time.time())}:R>""")
                await db.execute("UPDATE config SET bot_role_id = ? WHERE guild = ?", role.id, ctx.guild.id)
                await response.edit(content=f":white_check_mark:  **BOT ROLE SET TO {role.mention}**")
            elif option.lower() == "human_role":
                await response.edit(content=f""":gear:  **DEKKO is executing an SQL query...**
Query: `UPDATE config SET human_role_id = {role.id} WHERE guild = {ctx.guild.id}`
Requested by: `DEKKO Command Processor`
Started: <t:{int(time.time())}:R>""")
                await db.execute("UPDATE config SET human_role_id = ? WHERE guild = ?", role.id, ctx.guild.id)
                await response.edit(content=f":white_check_mark:  **HUMAN ROLE SET TO {role.mention}**")
            elif option.lower() == "verified_role":
                await response.edit(content=f""":gear:  **DEKKO is executing an SQL query...**
Query: `UPDATE config SET verified_role_id = {role.id} WHERE guild = {ctx.guild.id}`
Requested by: `DEKKO Command Processor`
Started: <t:{int(time.time())}:R>""")
                await db.execute("UPDATE config SET verified_role_id = ? WHERE guild = ?", role.id, ctx.guild.id)
                await response.edit(content=f":white_check_mark:  **VERIFIED ROLE SET TO {role.mention}**")
            elif option.lower() == "muted_role":
                await response.edit(content=f""":gear:  **DEKKO is executing an SQL query...**
Query: `UPDATE config SET mute_role_id = {role.id} WHERE guild = {ctx.guild.id}`
Requested by: `DEKKO Command Processor`
Started: <t:{int(time.time())}:R>""")
                await db.execute("UPDATE config SET mute_role_id = ? WHERE guild = ?", role.id, ctx.guild.id)
                await response.edit(content=f":white_check_mark:  **MUTED ROLE SET TO {role.mention}**")
            elif option.lower() == "purgatory_role":
                await response.edit(content=f""":gear:  **DEKKO is executing an SQL query...**
Query: `UPDATE config SET purgatory_role_id = {role.id} WHERE guild = {ctx.guild.id}`
Requested by: `DEKKO Command Processor`
Started: <t:{int(time.time())}:R>""")
                await db.execute("UPDATE config SET purgatory_role_id = ? WHERE guild = ?", role.id, ctx.guild.id)
                await response.edit(content=f":white_check_mark:  **PURGATORY ROLE SET TO {role.mention}**")
            elif option.lower() == "sus_role":
                await response.edit(content=f""":gear:  **DEKKO is executing an SQL query...**
Query: `UPDATE config SET sus_role_id = {role.id} WHERE guild = {ctx.guild.id}`
Requested by: `DEKKO Command Processor`
Started: <t:{int(time.time())}:R>""")
                await db.execute("UPDATE config SET sus_role_id = ? WHERE guild = ?", role.id, ctx.guild.id)
                await response.edit(content=f":white_check_mark:  **SUS ROLE SET TO {role.mention}**")
            else:
                await response.edit(content=":warning:  **INVALID OPTION**")

    @_setup_roles.error
    async def _edit_role_config_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send(""":no_entry:  **ACCESS DENIED CYKA**```java
Exception in thread "main" java.lang.SecurityException: Permission Denial
\tat me.declanz.DEKKO(bot.java:249)
\tat me.declanz.DEKKO.PermissionCheck(events.java:12)
\tat me.declanz.DEKKO.setup(setup.java:153)
```""")

            await self.bot.get_channel(await db.fetch_one("SELECT error_channel FROM config WHERE guild = ?", ctx.guild.id)).send(""":no_entry:  **AN ERROR HAS OCCURED**```java
Exception in thread "main" java.lang.SecurityException: Permission Denial
\tat me.declanz.DEKKO(bot.java:249)
\tat me.declanz.DEKKO.PermissionCheck(events.java:12)
\tat me.declanz.DEKKO.setup(setup.java:153)
```""")
            
    @_setup.command(name='holidays', invoke_without_subcommand=True, with_app_command=True)
    @app_commands.allowed_installs(guilds=True, users=False)
    @app_commands.allowed_contexts(guilds=True, dms=False, private_channels=True)
    @commands.has_permissions(administrator=True)
    async def _setup_holidays(self, ctx, *, option: str, channel: discord.abc.GuildChannel):
        """Edits a holiday configuration option"""

        async with ctx.typing():
            response = await ctx.send(":hourglass:  **Please wait...**")

            if option.lower() == "new_years_channel":
                await response.edit(content=f""":gear:  **DEKKO is executing an SQL query...**
Query: `UPDATE config SET new_years_channel = {channel.id} WHERE guild = {ctx.guild.id}`
Requested by: `DEKKO Command Processor`
Started: <t:{int(time.time())}:R>""")
                await db.execute("UPDATE config SET new_years_channel = ? WHERE guild = ?", channel.id, ctx.guild.id)
                await response.edit(content=f":white_check_mark:  **NEW YEARS CHANNEL SET TO {channel.mention}**")
            elif option.lower() == "chinese_new_years_channel":
                await response.edit(content=f""":gear:  **DEKKO is executing an SQL query...**
Query: `UPDATE config SET cn_new_years_channel = {channel.id} WHERE guild = {ctx.guild.id}`
Requested by: `DEKKO Command Processor`
Started: <t:{int(time.time())}:R>""")
                await db.execute("UPDATE config SET cn_new_years_channel = ? WHERE guild = ?", channel.id, ctx.guild.id)
                await response.edit(content=f":white_check_mark:  **CHINESE NEW YEARS CHANNEL SET TO {channel.mention}**")
            elif option.lower() == "valentines_channel":
                await response.edit(content=f""":gear:  **DEKKO is executing an SQL query...**
Query: `UPDATE config SET vday_channel = {channel.id} WHERE guild = {ctx.guild.id}`
Requested by: `DEKKO Command Processor`
Started: <t:{int(time.time())}:R>""")
                await db.execute("UPDATE config SET vday_channel = ? WHERE guild = ?", channel.id, ctx.guild.id)
                await response.edit(content=f":white_check_mark:  **VALENTINES DAY CHANNEL SET TO {channel.mention}**")
            elif option.lower() == "st_patricks_channel":
                await response.edit(content=f""":gear:  **DEKKO is executing an SQL query...**
Query: `UPDATE config SET st_patricks_channel = {channel.id} WHERE guild = {ctx.guild.id}`
Requested by: `DEKKO Command Processor`
Started: <t:{int(time.time())}:R>""")
                await db.execute("UPDATE config SET st_patricks_channel = ? WHERE guild = ?", channel.id, ctx.guild.id)
                await response.edit(content=f":white_check_mark:  **ST. PATRICKS DAY CHANNEL SET TO {channel.mention}**")
            elif option.lower() == "easter_channel":
                await response.edit(content=f""":gear:  **DEKKO is executing an SQL query...**
Query: `UPDATE config SET easter_channel = {channel.id} WHERE guild = {ctx.guild.id}`
Requested by: `DEKKO Command Processor`
Started: <t:{int(time.time())}:R>""")
                await db.execute("UPDATE config SET easter_channel = ? WHERE guild = ?", channel.id, ctx.guild.id)
                await response.edit(content=f":white_check_mark:  **EASTER CHANNEL SET TO {channel.mention}**")
            elif option.lower() == "cinco_de_mayo_channel":
                await response.edit(content=f""":gear:  **DEKKO is executing an SQL query...**
Query: `UPDATE config SET cinco_de_mayo_channel = {channel.id} WHERE guild = {ctx.guild.id}`
Requested by: `DEKKO Command Processor`
Started: <t:{int(time.time())}:R>""")
                await db.execute("UPDATE config SET cinco_de_mayo_channel = ? WHERE guild = ?", channel.id, ctx.guild.id)
                await response.edit(content=f":white_check_mark:  **CINCO DE MAYO CHANNEL SET TO {channel.mention}**")
            elif option.lower() == "independence_day_channel":
                await response.edit(content=f""":gear:  **DEKKO is executing an SQL query...**
Query: `UPDATE config SET j4_channel = {channel.id} WHERE guild = {ctx.guild.id}`
Requested by: `DEKKO Command Processor`
Started: <t:{int(time.time())}:R>""")
                await db.execute("UPDATE config SET j4_channel = ? WHERE guild = ?", channel.id, ctx.guild.id)
                await response.edit(content=f":white_check_mark:  **INDEPENDENCE DAY CHANNEL SET TO {channel.mention}**")
            elif option.lower() == "halloween_channel":
                await response.edit(content=f""":gear:  **DEKKO is executing an SQL query...**
Query: `UPDATE config SET halloween_channel = {channel.id} WHERE guild = {ctx.guild.id}`
Requested by: `DEKKO Command Processor`
Started: <t:{int(time.time())}:R>""")
                await db.execute("UPDATE config SET halloween_channel = ? WHERE guild = ?", channel.id, ctx.guild.id)
                await response.edit(content=f":white_check_mark:  **HALLOWEEN CHANNEL SET TO {channel.mention}**")
            elif option.lower() == "thanksgiving_channel":
                await response.edit(content=f""":gear:  **DEKKO is executing an SQL query...**
Query: `UPDATE config SET thanksgiving_channel = {channel.id} WHERE guild = {ctx.guild.id}`
Requested by: `DEKKO Command Processor`
Started: <t:{int(time.time())}:R>""")
                await db.execute("UPDATE config SET thanksgiving_channel = ? WHERE guild = ?", channel.id, ctx.guild.id)
                await response.edit(content=f":white_check_mark:  **THANKSGIVING CHANNEL SET TO {channel.mention}**")
            elif option.lower() == "christmas_channel":
                await response.edit(content=f""":gear:  **DEKKO is executing an SQL query...**
Query: `UPDATE config SET christmas_channel = {channel.id} WHERE guild = {ctx.guild.id}`
Requested by: `DEKKO Command Processor`
Started: <t:{int(time.time())}:R>""")
                await db.execute("UPDATE config SET christmas_channel = ? WHERE guild = ?", channel.id, ctx.guild.id)
                await response.edit(content=f":white_check_mark:  **CHRISTMAS CHANNEL SET TO {channel.mention}**")
            elif option.lower() == "wishlist_channel":
                await response.edit(content=f""":gear:  **DEKKO is executing an SQL query...**
Query: `UPDATE config SET wishlist_channel = {channel.id} WHERE guild = {ctx.guild.id}`
Requested by: `DEKKO Command Processor`
Started: <t:{int(time.time())}:R>""")
                await db.execute("UPDATE config SET wishlist_channel = ? WHERE guild = ?", channel.id, ctx.guild.id)
                await response.edit(content=f":white_check_mark:  **WISHLIST CHANNEL SET TO {channel.mention}**")
            else:
                await response.edit(content=":warning:  **INVALID OPTION**")


async def setup(bot):
    bot.add_cog(Setup(bot))