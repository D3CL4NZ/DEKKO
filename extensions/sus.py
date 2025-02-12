import discord
from discord import app_commands
from discord.ext import commands

import common

import time

from database import db

class SuspiciousUsers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.initialize_database())

    async def initialize_database(self):
        common.logger.info("[Suspicious Users] Initializing database...")
        await db.execute("CREATE TABLE IF NOT EXISTS `naughty_list` (user_id INTEGER PRIMARY KEY, username TEXT, reason TEXT)")
        common.logger.info("[Suspicious Users] Successfully loaded suspicious users database.")

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        if not after.bot:
            if before.pending and not after.pending:
                sus_role = after.guild.get_role(await db.fetch_one("SELECT sus_role_id FROM config WHERE guild = ?", after.guild.id))
                purgatory_role = after.guild.get_role(await db.fetch_one("SELECT purgatory_role_id FROM config WHERE guild = ?", after.guild.id))
                moderator_role = after.guild.get_role(await db.fetch_one("SELECT mod_role_id FROM config WHERE guild = ?", after.guild.id))

                log_channel = self.bot.get_channel(await db.fetch_one("SELECT log_channel FROM config WHERE guild = ?", after.guild.id))
                admin_channel = self.bot.get_channel(await db.fetch_one("SELECT admin_channel FROM config WHERE guild = ?", after.guild.id))
                manver_channel = self.bot.get_channel(await db.fetch_one("SELECT manver_channel FROM config WHERE guild = ?", after.guild.id))

                await after.edit(roles=[purgatory_role])
                
                verification_message = await manver_channel.send(f"""||@everyone|| {moderator_role.mention}
**A user is waiting to be verified**

User: {after.mention}
Accepted rules: `True` :white_check_mark:
Reputation check: `Pass` :white_check_mark:
Sus check: `In progress...` :hourglass:""")

                sus_users = []

                # Fetch suspicious users table from the database
                data = await db.fetch("SELECT * FROM naughty_list")

                # Check if the user is in the suspicious users table
                for user in data:
                    if after.id == user[0]:
                        await after.edit(roles=[sus_role, purgatory_role])
                        
                        await verification_message.edit(content=f"""||@everyone|| {moderator_role.mention}
**A user is waiting to be verified**

User: {after.mention}
Accepted rules: `True` :white_check_mark:
Reputation check: `Pass` :white_check_mark:
Sus check: `FAIL` :x:""")
                        
                        await admin_channel.send(":rotating_light: :rotating_light: **ATTENTION: A SUSPICIOUS USER HAS JOINED THE SERVER.**")
                        await manver_channel.send(f""":rotating_light: **ATTENTION: ACCOUNT {after.mention} IS ON THE NAUGHTY LIST** :rotating_light:

**Reason:** [BAN SYNC] User is currently banned from another DEKKO-Secured server: `Военные без границ`""")

                        embed = discord.Embed(
                            title=None,
                            description=f":rotating_light: {after.mention} **is on the naughty list**",
                            color=discord.Colour.red()
                        )
                        embed.set_author(name=after.name, icon_url=after.display_avatar.url)
                        embed.set_thumbnail(url=after.display_avatar.url)
                        embed.timestamp = discord.utils.utcnow()
                        embed.set_footer(text="User ID: {}".format(after.id))

                        await log_channel.send(embed=embed)
                        return

                await verification_message.edit(content=f"""||@everyone|| {moderator_role.mention}
**A user is waiting to be verified**

User: {after.mention}
Accepted rules: `True` :white_check_mark:
Reputation check: `Pass` :white_check_mark:
Sus check: `Pass` :white_check_mark:""")

                await after.guild.system_channel.send(f"\u0434\u043e\u0431\u0440\u043e \u043f\u043e\u0436\u0430\u043b\u043e\u0432\u0430\u0442\u044c, {after.mention}!")

    @commands.hybrid_command(name='naughtylist', with_app_command=True)
    @app_commands.allowed_installs(guilds=True, users=False)
    @app_commands.allowed_contexts(guilds=True, dms=False, private_channels=True)
    @commands.has_permissions(moderate_members=True)
    async def _naughtlylist(self, ctx):
        sus_users = []

        data = await db.fetch("SELECT * FROM naughty_list")

        for user in data:
            sus_users.append("<@{}> (`{}`)".format(str(user[0]), user[1]))

        sus_users_string = '\n'.join(sus_users)

        await ctx.send("""**__THE NAUGHTY LIST__**

{}""".format(sus_users_string))

    @commands.hybrid_command(name='sus', with_app_command=True)
    @app_commands.allowed_installs(guilds=True, users=False)
    @app_commands.allowed_contexts(guilds=True, dms=False, private_channels=True)
    @commands.has_permissions(moderate_members=True)
    async def _sus(self, ctx, *, user: discord.User):
        """Manually flags a user as suspicious"""

        async with ctx.typing():
            response = await ctx.send(":hourglass:  **Please wait...**")

            log_channels = await db.fetch("SELECT log_channel FROM config")
            
            if user.id == self.bot.user.id:
                await response.edit(content="Bite me.")
                return

            # Check if the user is already marked as sus
            sus_users = []
            data = await db.fetch("SELECT * FROM naughty_list")

            await response.edit(content=f""":gear:  **DEKKO is executing an SQL query...**
Query: `SELECT * FROM naughty_list`
Requested by: `DEKKO Command Processor`
Started: <t:{int(time.time())}:R>""")

            for u in data:
                sus_users.append(u[0])
            if user.id in sus_users:
                await response.edit(content=f":warning: User {user.mention} is already on the naughty list.")
                return

            await db.execute("INSERT INTO naughty_list VALUES (?, ?)", user.id, user.name)

            await response.edit(content=f""":gear:  **DEKKO is executing an SQL query...**
Query: `INSERT INTO naughty_list VALUES ({user.id}, {user.name})`
Requested by: `DEKKO Command Processor`
Started: <t:{int(time.time())}:R>""")

            if ctx.guild.get_member(user.id) is not None:
                sus_role = user.guild.get_role(await db.fetch_one("SELECT sus_role_id FROM config WHERE guild = ?", user.guild.id))
                purgatory_role = user.guild.get_role(await db.fetch_one("SELECT purgatory_role_id FROM config WHERE guild = ?", user.guild.id))

                if purgatory_role not in user.roles and sus_role not in user.roles:
                    await user.edit(roles=[purgatory_role, sus_role])

            embed = discord.Embed(description=f"{user.mention} **has been added to the naughty list.**", color=discord.Colour.red())

            for log_channel_id in log_channels:
                log_channel = self.bot.get_channel(log_channel_id)

                log_embed = discord.Embed(
                    title=None,
                    description=f":triangular_flag_on_post: {user.mention} **was added to the naughty list**",
                    color=discord.Colour.red()
                )
                log_embed.set_author(name=user.name, icon_url=user.display_avatar.url)
                log_embed.set_thumbnail(url=user.display_avatar.url)
                log_embed.timestamp = discord.utils.utcnow()
                log_embed.set_footer(text=f"User ID: {user.id}")

                await log_channel.send(embed=log_embed)

            await response.edit(content=":pencil: Database transaction successful.", embed=embed)

    @_sus.error
    async def _sus_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send(""":no_entry:  **ACCESS DENIED CYKA**```java
Exception in thread "main" java.lang.SecurityException: Permission Denial
\tat me.declanz.DEKKO(bot.java:249)
\tat me.declanz.DEKKO.PermissionCheck(events.java:12)
\tat me.declanz.DEKKO.sus(sus.java:33)
```""")

            await self.bot.get_channel(await db.fetch_one("SELECT error_channel FROM config WHERE guild = ?", ctx.guild.id)).send(""":no_entry:  **AN ERROR HAS OCCURED**```java
Exception in thread "main" java.lang.SecurityException: Permission Denial
\tat me.declanz.DEKKO(bot.java:249)
\tat me.declanz.DEKKO.PermissionCheck(events.java:12)
\tat me.declanz.DEKKO.sus(sus.java:33)
```""")

    @commands.hybrid_command(name='unsus', with_app_command=True)
    @app_commands.allowed_installs(guilds=True, users=False)
    @app_commands.allowed_contexts(guilds=True, dms=False, private_channels=True)
    @commands.has_permissions(moderate_members=True)
    async def _unsus(self, ctx, *, user: discord.User):
        """Unflags a suspicious user"""

        async with ctx.typing():
            response = await ctx.send(":hourglass:  **Please wait...**")

            log_channels = await db.fetch("SELECT log_channel FROM config")
            
            if user.id == self.bot.user.id:
                await response.edit(content="Bite me.")
                return

            # Check if the user not already marked as sus
            sus_users = []

            await response.edit(content=f""":gear:  **DEKKO is executing an SQL query...**
Query: `SELECT * FROM naughty_list`
Requested by: `DEKKO Command Processor`
Started: <t:{int(time.time())}:R>""")

            data = await db.fetch("SELECT * FROM naughty_list")

            for u in data:
                sus_users.append(u[0])
            if user.id not in sus_users:
                await response.edit(content=f":warning: {user.id} is not on the naughty list.")
                return

            await response.edit(content=f""":gear:  **DEKKO is executing an SQL query...**
Query: `DELETE FROM naughty_list WHERE user_id = {user.id}`
Requested by: `DEKKO Command Processor`
Started: <t:{int(time.time())}:R>""")

            await db.execute("DELETE FROM naughty_list WHERE user_id = ?", user.id)

            if ctx.guild.get_member(user.id) is not None:
                sus_role = user.guild.get_role(await db.fetch_one("SELECT sus_role_id FROM config WHERE guild = ?", user.guild.id))
                purgatory_role = user.guild.get_role(await db.fetch_one("SELECT purgatory_role_id FROM config WHERE guild = ?", user.guild.id))

                if purgatory_role in user.roles and sus_role in user.roles:
                    await user.edit(roles=[purgatory_role])

            embed = discord.Embed(description=f"{user.mention} **has been removed from the naughty list.**", color=discord.Colour.green())

            for log_channel_id in log_channels:
                log_channel = self.bot.get_channel(log_channel_id)

                log_embed = discord.Embed(
                    title=None,
                    description=f":flag_white: {user.mention} **was removed from the naughty list**",
                    color=discord.Colour.green()
                )
                log_embed.set_author(name=user.name, icon_url=user.display_avatar.url)
                log_embed.set_thumbnail(url=user.display_avatar.url)
                log_embed.timestamp = discord.utils.utcnow()
                log_embed.set_footer(text="User ID: {}".format(user.id))

                await log_channel.send(embed=log_embed)

            await response.edit(content=":pencil: Database transaction successful.", embed=embed)

    @_unsus.error
    async def _unsus_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send(""":no_entry:  **ACCESS DENIED CYKA**```java
Exception in thread "main" java.lang.SecurityException: Permission Denial
\tat me.declanz.DEKKO(bot.java:249)
\tat me.declanz.DEKKO.PermissionCheck(events.java:12)
\tat me.declanz.DEKKO.sus(sus.java:33)
```""")

            await self.bot.get_channel(await db.fetch_one("SELECT error_channel FROM config WHERE guild = ?", ctx.guild.id)).send(""":no_entry:  **AN ERROR HAS OCCURED**```java
Exception in thread "main" java.lang.SecurityException: Permission Denial
\tat me.declanz.DEKKO(bot.java:249)
\tat me.declanz.DEKKO.PermissionCheck(events.java:12)
\tat me.declanz.DEKKO.sus(sus.java:33)
```""")

async def setup(bot):
        await bot.add_cog(SuspiciousUsers(bot))
