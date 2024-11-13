import discord
from discord import app_commands
from discord.ext import tasks, commands
import sqlite3
import aiohttp

import config

import time

database = sqlite3.connect('suspicious_users.db')
cursor = database.cursor()

class SuspiciousUsers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("[Suspicious Users] Initializing database...")
        database.execute("CREATE TABLE IF NOT EXISTS users(user_id INTEGER, username STRING)")
        print("[Suspicious Users] Successfully loaded suspicious users database.")
        self.sus_users_update_timer.start()

    def cog_unload(self):
        self.sus_users_update_timer.cancel()

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        if not after.bot:
            if before.pending and not after.pending:
                sus_role = discord.utils.get(after.guild.roles, name='Suspicious User')
                purgatory_role = discord.utils.get(after.guild.roles, name='purgatory')
                moderator_role = discord.utils.get(after.guild.roles, name='Moderator')

                log_channel = self.bot.get_channel(config.LOG_CHANNEL_ID)
                admin_channel = self.bot.get_channel(config.ADMIN_CHANNEL_ID)
                manver_channel = self.bot.get_channel(config.MANVER_CHANNEL_ID)

                await after.edit(roles=[purgatory_role])
                
                verification_message = await manver_channel.send(f"""||@everyone|| {moderator_role.mention}
**A user is waiting to be verified**

User: {after.mention}
Accepted rules: `True` :white_check_mark:
Reputation check: `Pass` :white_check_mark:
Sus check: `In progress...` :hourglass:""")

                sus_users = []

                # Fetch suspicious users table from the database
                query = "SELECT * FROM users"
                data = cursor.execute(query).fetchall()

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


    @tasks.loop(hours=1.0)
    async def sus_users_update_timer(self):
        self.bot.dispatch("sus_users_updated")

    @sus_users_update_timer.before_loop
    async def before_sus_users_update_timer(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_sus_users_updated(self):
        sus_users = []

        query = "SELECT * FROM users"
        data = cursor.execute(query).fetchall()

        for user in data:
            sus_users.append("<@{}> (`{}`)".format(str(user[0]), user[1]))

        sus_users_string = '\n'.join(sus_users)

        async with aiohttp.ClientSession() as session:
            webhook = discord.Webhook.from_url(config.SUS_WEBHOOK_URL, session=session)
            await webhook.edit_message(config.SUS_LIST_ID, content="""**__THE NAUGHTY LIST__**

{}""".format(sus_users_string))

    @commands.hybrid_command(name='sus', with_app_command=True)
    @app_commands.allowed_installs(guilds=True, users=False)
    @app_commands.allowed_contexts(guilds=True, dms=False, private_channels=True)
    @commands.has_any_role("supreme leader", "administrator", "moderator", "Supreme Leader", "Administrator", "Moderator")
    async def _sus(self, ctx, *, user: discord.User):
        """Manually flags a user as suspicious"""

        async with ctx.typing():
            response = await ctx.send(":hourglass:  **Please wait...**")

            log_channel = self.bot.get_channel(config.LOG_CHANNEL_ID)
            
            if user.id == self.bot.user.id:
                await response.edit(content="Bite me.")
                return

            # Check if the user is already marked as sus
            sus_users = []
            query = "SELECT * FROM users"
            data = cursor.execute(query).fetchall()

            await response.edit(content=f""":gear:  **DEKKO is executing an SQL query...**
Query: `SELECT * FROM users`
Requested by: `DEKKO Command Processor`
Started: <t:{int(time.time())}:R>""")

            for u in data:
                sus_users.append(u[0])
            if user.id in sus_users:
                await response.edit(content=f":warning: User {user.mention} is already on the naughty list.")
                return

            query = "INSERT INTO users VALUES (?, ?)"
            cursor.execute(query, (user.id, user.name))
            database.commit()

            await response.edit(content=f""":gear:  **DEKKO is executing an SQL query...**
Query: `INSERT INTO users VALUES ({user.id}, {user.name})`
Requested by: `DEKKO Command Processor`
Started: <t:{int(time.time())}:R>""")

            if ctx.guild.get_member(user.id) is not None:
                purgatory_role = discord.utils.get(user.guild.roles, name='purgatory')
                sus_role = discord.utils.get(user.guild.roles, name='Suspicious User')

                if purgatory_role not in user.roles and sus_role not in user.roles:
                    await user.edit(roles=[purgatory_role, sus_role])

            embed = discord.Embed(description=f"{user.mention} **has been added to the naughty list.**", color=discord.Colour.red())

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

            await self.bot.dispatch("sus_users_updated")

    @_sus.error
    async def _sus_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send(""":no_entry:  **ACCESS DENIED CYKA**```java
Exception in thread "main" java.lang.SecurityException: Permission Denial
\tat me.declanz.DEKKO(bot.java:249)
\tat me.declanz.DEKKO.PermissionCheck(events.java:12)
\tat me.declanz.DEKKO.sus(sus.java:33)
```""")

            await self.bot.get_channel(config.ERROR_CHANNEL_ID).send(""":no_entry:  **AN ERROR HAS OCCURED**```java
Exception in thread "main" java.lang.SecurityException: Permission Denial
\tat me.declanz.DEKKO(bot.java:249)
\tat me.declanz.DEKKO.PermissionCheck(events.java:12)
\tat me.declanz.DEKKO.sus(sus.java:33)
```""")

    @commands.hybrid_command(name='unsus', with_app_command=True)
    @app_commands.allowed_installs(guilds=True, users=False)
    @app_commands.allowed_contexts(guilds=True, dms=False, private_channels=True)
    @commands.has_any_role("supreme leader", "administrator", "moderator", "Supreme Leader", "Administrator", "Moderator")
    async def _unsus(self, ctx, *, user: discord.User):
        """Unflags a suspicious user"""

        async with ctx.typing():
            response = await ctx.send(":hourglass:  **Please wait...**")

            log_channel = self.bot.get_channel(config.LOG_CHANNEL_ID)
            
            if user.id == self.bot.user.id:
                await response.edit(content="Bite me.")
                return

            # Check if the user not already marked as sus
            sus_users = []
            query = "SELECT * FROM users"
            data = cursor.execute(query).fetchall()

            await response.edit(content=f""":gear:  **DEKKO is executing an SQL query...**
Query: `SELECT * FROM users`
Requested by: `DEKKO Command Processor`
Started: <t:{int(time.time())}:R>""")

            for u in data:
                sus_users.append(u[0])
            if user.id not in sus_users:
                await response.edit(content=f":warning: {user.id} is not on the naughty list.")
                return

            query = "DELETE FROM users WHERE user_id = ?"
            cursor.execute(query, (user.id,))
            database.commit()

            await response.edit(content=f""":gear:  **DEKKO is executing an SQL query...**
Query: `DELETE FROM users WHERE user_id = {user.id}`
Requested by: `DEKKO Command Processor`
Started: <t:{int(time.time())}:R>""")

            if ctx.guild.get_member(user.id) is not None:
                purgatory_role = discord.utils.get(user.guild.roles, name='purgatory')
                sus_role = discord.utils.get(user.guild.roles, name='Suspicious User')

                if purgatory_role in user.roles and sus_role in user.roles:
                    await user.edit(roles=[purgatory_role])

            embed = discord.Embed(description=f"{user.mention} **has been removed from the naughty list.**", color=discord.Colour.green())

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

            await self.bot.dispatch("sus_users_updated")

    @_unsus.error
    async def _unsus_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send(""":no_entry:  **ACCESS DENIED CYKA**```java
Exception in thread "main" java.lang.SecurityException: Permission Denial
\tat me.declanz.DEKKO(bot.java:249)
\tat me.declanz.DEKKO.PermissionCheck(events.java:12)
\tat me.declanz.DEKKO.sus(sus.java:33)
```""")

            await self.bot.get_channel(config.ERROR_CHANNEL_ID).send(""":no_entry:  **AN ERROR HAS OCCURED**```java
Exception in thread "main" java.lang.SecurityException: Permission Denial
\tat me.declanz.DEKKO(bot.java:249)
\tat me.declanz.DEKKO.PermissionCheck(events.java:12)
\tat me.declanz.DEKKO.sus(sus.java:33)
```""")

async def setup(bot):
        await bot.add_cog(SuspiciousUsers(bot))
