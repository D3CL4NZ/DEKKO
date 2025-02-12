import discord
from discord import app_commands
from discord.ext import commands

import time

import common

from database import db

class SetupDB(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='dekkosetup', with_app_command=True)
    @app_commands.allowed_installs(guilds=True, users=False)
    @app_commands.allowed_contexts(guilds=True, dms=False, private_channels=True)
    @commands.has_permissions(administrator=True)
    async def _dekkosetup(self, ctx, *, subcommand: str, option: str=None, value: str=None):
        """Configures DEKKO for your server"""

        if subcommand is None:
            return await ctx.send(':warning:  **You must specify a subcommand**')

        async with ctx.typing():
            response = await ctx.send(":hourglass:  **Please wait...**")

            if subcommand.lower() == "initialize":
                # Check if the guild already exists in the database
                existing_config = await db.fetch_one("SELECT * FROM config WHERE guild = ?", ctx.guild.id)
                existing_holidata = await db.fetch_one("SELECT * FROM holidata WHERE guild = ?", ctx.guild.id)

                if existing_config or existing_holidata:
                    await response.edit(content=":warning:  **DATABASE ALREADY INITIALIZED FOR THIS SERVER**")
                    return

                await db.execute("INSERT INTO config (guild) VALUES (?)", ctx.guild.id)
                await db.execute("INSERT INTO holidata (guild) VALUES (?)", ctx.guild.id)

                await response.edit(content=":white_check_mark:  **INITIALIZED DATABASE**")
            elif subcommand.lower() == "channels":
                if option.lower() == "log_channel":
                    await response.edit(content=f""":gear:  **DEKKO is executing an SQL query...**
    Query: `UPDATE config SET log_channel = {value} WHERE guild = {ctx.guild.id}`
    Requested by: `DEKKO Command Processor`
    Started: <t:{int(time.time())}:R>""")
                    await db.execute("UPDATE config SET log_channel = ? WHERE guild = ?", value, ctx.guild.id)
                    await response.edit(content=f":white_check_mark:  **LOG CHANNEL SET TO <#{value}>**")
                elif option.lower() == "error_channel":
                    await response.edit(content=f""":gear:  **DEKKO is executing an SQL query...**
    Query: `UPDATE config SET error_channel = {value} WHERE guild = {ctx.guild.id}`
    Requested by: `DEKKO Command Processor`
    Started: <t:{int(time.time())}:R>""")
                    await db.execute("UPDATE config SET error_channel = ? WHERE guild = ?", value, ctx.guild.id)
                    await response.edit(content=f":white_check_mark:  **ERROR CHANNEL SET TO <#{value}>**")
                elif option.lower() == "admin_channel":
                    await response.edit(content=f""":gear:  **DEKKO is executing an SQL query...**
    Query: `UPDATE config SET admin_channel = {value} WHERE guild = {ctx.guild.id}`
    Requested by: `DEKKO Command Processor`
    Started: <t:{int(time.time())}:R>""")
                    await db.execute("UPDATE config SET admin_channel = ? WHERE guild = ?", value, ctx.guild.id)
                    await response.edit(content=f":white_check_mark:  **ADMIN CHANNEL SET TO <#{value}>**")
                elif option.lower() == "verification_channel":
                    await response.edit(content=f""":gear:  **DEKKO is executing an SQL query...**
    Query: `UPDATE config SET manver_channel = {value} WHERE guild = {ctx.guild.id}`
    Requested by: `DEKKO Command Processor`
    Started: <t:{int(time.time())}:R>""")
                    await db.execute("UPDATE config SET manver_channel = ? WHERE guild = ?", value, ctx.guild.id)
                    await response.edit(content=f":white_check_mark:  **VERIFICATION CHANNEL SET TO <#{value}>**")
                else:
                    await response.edit(content=":warning:  **INVALID OPTION**")
            elif subcommand.lower() == "roles":
                if option.lower() == "owner_role":
                    await response.edit(content=f""":gear:  **DEKKO is executing an SQL query...**
    Query: `UPDATE config SET owner_role_id = {value} WHERE guild = {ctx.guild.id}`
    Requested by: `DEKKO Command Processor`
    Started: <t:{int(time.time())}:R>""")
                    await db.execute("UPDATE config SET owner_role_id = ? WHERE guild = ?", value, ctx.guild.id)
                    await response.edit(content=f":white_check_mark:  **OWNER ROLE SET TO <@&{value}>**")
                elif option.lower() == "admin_role":
                    await response.edit(content=f""":gear:  **DEKKO is executing an SQL query...**
    Query: `UPDATE config SET admin_role_id = {value} WHERE guild = {ctx.guild.id}`
    Requested by: `DEKKO Command Processor`
    Started: <t:{int(time.time())}:R>""")
                    await db.execute("UPDATE config SET admin_role_id = ? WHERE guild = ?", value, ctx.guild.id)
                    await response.edit(content=f":white_check_mark:  **ADMIN ROLE SET TO <@&{value}>**")
                elif option.lower() == "moderator_role":
                    await response.edit(content=f""":gear:  **DEKKO is executing an SQL query...**
    Query: `UPDATE config SET mod_role_id = {value} WHERE guild = {ctx.guild.id}`
    Requested by: `DEKKO Command Processor`
    Started: <t:{int(time.time())}:R>""")
                    await db.execute("UPDATE config SET mod_role_id = ? WHERE guild = ?", value, ctx.guild.id)
                    await response.edit(content=f":white_check_mark:  **MODERATOR ROLE SET TO <@&{value}>**")
                elif option.lower() == "bot_role":
                    await response.edit(content=f""":gear:  **DEKKO is executing an SQL query...**
    Query: `UPDATE config SET bot_role_id = {value} WHERE guild = {ctx.guild.id}`
    Requested by: `DEKKO Command Processor`
    Started: <t:{int(time.time())}:R>""")
                    await db.execute("UPDATE config SET bot_role_id = ? WHERE guild = ?", value, ctx.guild.id)
                    await response.edit(content=f":white_check_mark:  **BOT ROLE SET TO <@&{value}>**")
                elif option.lower() == "human_role":
                    await response.edit(content=f""":gear:  **DEKKO is executing an SQL query...**
    Query: `UPDATE config SET human_role_id = {value} WHERE guild = {ctx.guild.id}`
    Requested by: `DEKKO Command Processor`
    Started: <t:{int(time.time())}:R>""")
                    await db.execute("UPDATE config SET human_role_id = ? WHERE guild = ?", value, ctx.guild.id)
                    await response.edit(content=f":white_check_mark:  **HUMAN ROLE SET TO <@&{value}>**")
                elif option.lower() == "verified_role":
                    await response.edit(content=f""":gear:  **DEKKO is executing an SQL query...**
    Query: `UPDATE config SET verified_role_id = {value} WHERE guild = {ctx.guild.id}`
    Requested by: `DEKKO Command Processor`
    Started: <t:{int(time.time())}:R>""")
                    await db.execute("UPDATE config SET verified_role_id = ? WHERE guild = ?", value, ctx.guild.id)
                    await response.edit(content=f":white_check_mark:  **VERIFIED ROLE SET TO <@&{value}>**")
                elif option.lower() == "muted_role":
                    await response.edit(content=f""":gear:  **DEKKO is executing an SQL query...**
    Query: `UPDATE config SET mute_role_id = {value} WHERE guild = {ctx.guild.id}`
    Requested by: `DEKKO Command Processor`
    Started: <t:{int(time.time())}:R>""")
                    await db.execute("UPDATE config SET mute_role_id = ? WHERE guild = ?", value, ctx.guild.id)
                    await response.edit(content=f":white_check_mark:  **MUTED ROLE SET TO <@&{value}>**")
                elif option.lower() == "purgatory_role":
                    await response.edit(content=f""":gear:  **DEKKO is executing an SQL query...**
    Query: `UPDATE config SET purgatory_role_id = {value} WHERE guild = {ctx.guild.id}`
    Requested by: `DEKKO Command Processor`
    Started: <t:{int(time.time())}:R>""")
                    await db.execute("UPDATE config SET purgatory_role_id = ? WHERE guild = ?", value, ctx.guild.id)
                    await response.edit(content=f":white_check_mark:  **PURGATORY ROLE SET TO <@&{value}>**")
                elif option.lower() == "sus_role":
                    await response.edit(content=f""":gear:  **DEKKO is executing an SQL query...**
    Query: `UPDATE config SET sus_role_id = {value} WHERE guild = {ctx.guild.id}`
    Requested by: `DEKKO Command Processor`
    Started: <t:{int(time.time())}:R>""")
                    await db.execute("UPDATE config SET sus_role_id = ? WHERE guild = ?", value, ctx.guild.id)
                    await response.edit(content=f":white_check_mark:  **SUS ROLE SET TO <@&{value}>**")
                else:
                    await response.edit(content=":warning:  **INVALID OPTION**")
            elif subcommand.lower() == "holidays":
                if option.lower() == "new_years_channel":
                    await response.edit(content=f""":gear:  **DEKKO is executing an SQL query...**
    Query: `UPDATE holidata SET new_years_channel = {value} WHERE guild = {ctx.guild.id}`
    Requested by: `DEKKO Command Processor`
    Started: <t:{int(time.time())}:R>""")
                    await db.execute("UPDATE holidata SET new_years_channel = ? WHERE guild = ?", value, ctx.guild.id)
                    await response.edit(content=f":white_check_mark:  **NEW YEARS CHANNEL SET TO <#{value}>**")
                elif option.lower() == "chinese_new_years_channel":
                    await response.edit(content=f""":gear:  **DEKKO is executing an SQL query...**
    Query: `UPDATE holidata SET cn_new_years_channel = {value} WHERE guild = {ctx.guild.id}`
    Requested by: `DEKKO Command Processor`
    Started: <t:{int(time.time())}:R>""")
                    await db.execute("UPDATE holidata SET cn_new_years_channel = ? WHERE guild = ?", value, ctx.guild.id)
                    await response.edit(content=f":white_check_mark:  **CHINESE NEW YEARS CHANNEL SET TO <#{value}>**")
                elif option.lower() == "valentines_channel":
                    await response.edit(content=f""":gear:  **DEKKO is executing an SQL query...**
    Query: `UPDATE holidata SET vday_channel = {value} WHERE guild = {ctx.guild.id}`
    Requested by: `DEKKO Command Processor`
    Started: <t:{int(time.time())}:R>""")
                    await db.execute("UPDATE holidata SET vday_channel = ? WHERE guild = ?", value, ctx.guild.id)
                    await response.edit(content=f":white_check_mark:  **VALENTINES DAY CHANNEL SET TO <#{value}>**")
                elif option.lower() == "st_patricks_channel":
                    await response.edit(content=f""":gear:  **DEKKO is executing an SQL query...**
    Query: `UPDATE holidata SET st_patricks_channel = {value} WHERE guild = {ctx.guild.id}`
    Requested by: `DEKKO Command Processor`
    Started: <t:{int(time.time())}:R>""")
                    await db.execute("UPDATE holidata SET st_patricks_channel = ? WHERE guild = ?", value, ctx.guild.id)
                    await response.edit(content=f":white_check_mark:  **ST. PATRICKS DAY CHANNEL SET TO <#{value}>**")
                elif option.lower() == "easter_channel":
                    await response.edit(content=f""":gear:  **DEKKO is executing an SQL query...**
    Query: `UPDATE holidata SET easter_channel = {value} WHERE guild = {ctx.guild.id}`
    Requested by: `DEKKO Command Processor`
    Started: <t:{int(time.time())}:R>""")
                    await db.execute("UPDATE holidata SET easter_channel = ? WHERE guild = ?", value, ctx.guild.id)
                    await response.edit(content=f":white_check_mark:  **EASTER CHANNEL SET TO <#{value}>**")
                elif option.lower() == "cinco_de_mayo_channel":
                    await response.edit(content=f""":gear:  **DEKKO is executing an SQL query...**
    Query: `UPDATE holidata SET cinco_de_mayo_channel = {value} WHERE guild = {ctx.guild.id}`
    Requested by: `DEKKO Command Processor`
    Started: <t:{int(time.time())}:R>""")
                    await db.execute("UPDATE holidata SET cinco_de_mayo_channel = ? WHERE guild = ?", value, ctx.guild.id)
                    await response.edit(content=f":white_check_mark:  **CINCO DE MAYO CHANNEL SET TO <#{value}>**")
                elif option.lower() == "independence_day_channel":
                    await response.edit(content=f""":gear:  **DEKKO is executing an SQL query...**
    Query: `UPDATE holidata SET j4_channel = {value} WHERE guild = {ctx.guild.id}`
    Requested by: `DEKKO Command Processor`
    Started: <t:{int(time.time())}:R>""")
                    await db.execute("UPDATE holidata SET j4_channel = ? WHERE guild = ?", value, ctx.guild.id)
                    await response.edit(content=f":white_check_mark:  **INDEPENDENCE DAY CHANNEL SET TO <#{value}>**")
                elif option.lower() == "halloween_channel":
                    await response.edit(content=f""":gear:  **DEKKO is executing an SQL query...**
    Query: `UPDATE holidata SET halloween_channel = {value} WHERE guild = {ctx.guild.id}`
    Requested by: `DEKKO Command Processor`
    Started: <t:{int(time.time())}:R>""")
                    await db.execute("UPDATE holidata SET halloween_channel = ? WHERE guild = ?", value, ctx.guild.id)
                    await response.edit(content=f":white_check_mark:  **HALLOWEEN CHANNEL SET TO <#{value}>**")
                elif option.lower() == "thanksgiving_channel":
                    await response.edit(content=f""":gear:  **DEKKO is executing an SQL query...**
    Query: `UPDATE holidata SET thanksgiving_channel = {value} WHERE guild = {ctx.guild.id}`
    Requested by: `DEKKO Command Processor`
    Started: <t:{int(time.time())}:R>""")
                    await db.execute("UPDATE holidata SET thanksgiving_channel = ? WHERE guild = ?", value, ctx.guild.id)
                    await response.edit(content=f":white_check_mark:  **THANKSGIVING CHANNEL SET TO <#{value}>**")
                elif option.lower() == "christmas_channel":
                    await response.edit(content=f""":gear:  **DEKKO is executing an SQL query...**
    Query: `UPDATE holidata SET christmas_channel = {value} WHERE guild = {ctx.guild.id}`
    Requested by: `DEKKO Command Processor`
    Started: <t:{int(time.time())}:R>""")
                    await db.execute("UPDATE holidata SET christmas_channel = ? WHERE guild = ?", value, ctx.guild.id)
                    await response.edit(content=f":white_check_mark:  **CHRISTMAS CHANNEL SET TO <#{value}>**")
                elif option.lower() == "wishlist_channel":
                    await response.edit(content=f""":gear:  **DEKKO is executing an SQL query...**
    Query: `UPDATE holidata SET wishlist_channel = {value} WHERE guild = {ctx.guild.id}`
    Requested by: `DEKKO Command Processor`
    Started: <t:{int(time.time())}:R>""")
                    await db.execute("UPDATE holidata SET wishlist_channel = ? WHERE guild = ?", value, ctx.guild.id)
                    await response.edit(content=f":white_check_mark:  **WISHLIST CHANNEL SET TO <#{value}>**")
                else:
                    await response.edit(content=":warning:  **INVALID OPTION**")
            elif subcommand.lower() == "showconfig":
                await response.edit(content=f""":gear:  **DEKKO is executing an SQL query...**
    Query: `SELECT * FROM config WHERE guild = {ctx.guild.id}`
    Requested by: `DEKKO Command Processor`
    Started: <t:{int(time.time())}:R>""")
                config = await db.fetch_one("SELECT * FROM config WHERE guild = ?", ctx.guild.id)
                await response.edit(content=f""":gear:  **DEKKO is executing an SQL query...**
    Query: `SELECT * FROM holidata WHERE guild = {ctx.guild.id}`
    Requested by: `DEKKO Command Processor`
    Started: <t:{int(time.time())}:R>""")
                holidata = await db.fetch_one("SELECT * FROM holidata WHERE guild = ?", ctx.guild.id)

                if config and holidata:
                    embed = discord.Embed(
                        title=f"**Configuration for:** `{ctx.guild.name}`",
                        description=f"Guild ID: `{ctx.guild.id}`",
                        color=0xda00ff
                    )
                    embed.add_field(name="__**Channels**__", value=f"""Log Channel: {f"<#{config[1]}>" if config[1] else "`Not set`"}
Error Channel: {f"<#{config[2]}>" if config[2] else "`Not set`"}
Admin Channel: {f"<#{config[3]}>" if config[3] else "`Not set`"}
Verification Channel: {f"<#{config[4]}>" if config[4] else "`Not set`"}""", inline=False)
                    embed.add_field(name="__**Roles**__", value=f"""Owner Role: {f"<@&{config[6]}>" if config[6] else "`Not set`"}
Admin Role: {f"<@&{config[7]}>" if config[7] else "`Not set`"}
Moderator Role: {f"<@&{config[8]}>" if config[8] else "`Not set`"}
Bot Role: {f"<@&{config[9]}>" if config[9] else "`Not set`"}
Human Role: {f"<@&{config[10]}>" if config[10] else "`Not set`"}
Verified Role: {f"<@&{config[11]}>" if config[11] else "`Not set`"}
Muted Role: {f"<@&{config[12]}>" if config[12] else "`Not set`"}
Purgatory Role: {f"<@&{config[13]}>" if config[13] else "`Not set`"}
Sus Role: {f"<@&{config[14]}>" if config[14] else "`Not set`"}""", inline=False)
                    embed.add_field(name="__**Holidays**__", value=f"""New Years Channel: {f"<#{holidata[1]}>" if holidata[1] else "`Not set`"}
Chinese New Years Channel: {f"<#{holidata[2]}>" if holidata[2] else "`Not set`"}
Valentines Channel: {f"<#{holidata[3]}>" if holidata[3] else "`Not set`"}
St. Patricks Channel: {f"<#{holidata[4]}>" if holidata[4] else "`Not set`"}
Easter Channel: {f"<#{holidata[5]}>" if holidata[5] else "`Not set`"}
Cinco De Mayo Channel: {f"<#{holidata[6]}>" if holidata[6] else "`Not set`"}
Independence Day Channel: {f"<#{holidata[7]}>" if holidata[7] else "`Not set`"}
Halloween Channel: {f"<#{holidata[8]}>" if holidata[8] else "`Not set`"}
Thanksgiving Channel: {f"<#{holidata[9]}>" if holidata[9] else "`Not set`"}
Christmas Channel: {f"<#{holidata[10]}>" if holidata[10] else "`Not set`"}
Wishlist Channel: {f"<#{holidata[11]}>" if holidata[11] else "`Not set`"}""", inline=False)
                    embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon.url)
                    embed.set_footer(text=f"DEKKO! v{common.VERSION}")
                    embed.timestamp = discord.utils.utcnow()

                    await response.edit(content=":pencil: Database transaction successful.", embed=embed)
                else:
                    await response.edit(content=":warning:  **DATABASE NOT INITIALIZED**")
            else:
                await response.edit(content=":warning:  **INVALID SUBCOMMAND**")

    @commands.hybrid_command(name='dekkosetup-global', with_app_command=True)
    @app_commands.allowed_installs(guilds=True, users=False)
    @app_commands.allowed_contexts(guilds=True, dms=False, private_channels=True)
    @commands.is_owner()
    async def _dekkosetup_global(self, ctx, *, subcommand: str, option: str=None, value: str=None):
        """Changes global settings"""

        if subcommand is None:
            return await ctx.send(':warning:  **You must specify a subcommand**')
        
        async with ctx.typing():
            response = await ctx.send(":hourglass:  **Please wait...**")

            if subcommand.lower() == "channels":
                if option.lower() == "dm_channel":
                    await response.edit(content=f""":gear:  **DEKKO is executing an SQL query...**
    Query: `UPDATE global_config SET dm_channel = {value}`
    Requested by: `DEKKO Command Processor`
    Started: <t:{int(time.time())}:R>""")
                    await db.execute("UPDATE global_config SET dm_channel = ?", value)
                    await response.edit(content=f":white_check_mark:  **DM CHANNEL SET TO <#{value}>**")
                elif option.lower() == "global_log_channel":
                    await response.edit(content=f""":gear:  **DEKKO is executing an SQL query...**
    Query: `UPDATE global_config SET global_log_channel = {value}`
    Requested by: `DEKKO Command Processor`
    Started: <t:{int(time.time())}:R>""")
                    await db.execute("UPDATE global_config SET global_log_channel = ?", value)
                    await response.edit(content=f":white_check_mark:  **GLOBAL LOG CHANNEL SET TO <#{value}>**")
                else:
                    await response.edit(content=":warning:  **INVALID OPTION**")
            elif subcommand.lower() == "initialize-global":
                existing_config = await db.fetch_one("SELECT * FROM global_config WHERE id = ?", 1)

                if existing_config:
                    await response.edit(content=":warning:  **GLOBAL DATABASE ALREADY INITIALIZED**")
                    return

                await db.execute("INSERT INTO global_config (id) VALUES (?)", 1)

                await response.edit(content=":white_check_mark:  **INITIALIZED GLOBAL DATABASE**")
            else:
                await response.edit(content=":warning:  **INVALID SUBCOMMAND**")

async def setup(bot):
    await bot.add_cog(SetupDB(bot))