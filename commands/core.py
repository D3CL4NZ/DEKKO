import discord
from discord import app_commands
from discord.ext import commands

import os
import sys

import time

import common

from database import db

class Core(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='sync', with_app_command=True)
    @app_commands.allowed_installs(guilds=True, users=False)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @commands.is_owner()
    async def _sync(self, ctx):
        """Synchronizes the command tree"""

        log_channel_id = await db.fetch_one("SELECT global_log_channel FROM global_config")
        log_channel = self.bot.get_channel(log_channel_id[0]) if log_channel_id else None

        common.logger.info("Command tree sync requested...")

        async with ctx.typing():
            message = await ctx.send(""":hourglass:  **DEKKO is processing requests...**
Command: `{}`
Requested by: {}
Started: <t:{}:R>""".format(ctx.command, ctx.author.mention, int(time.time())))

            try:
                await self.bot.tree.sync()
            except Exception as e:
                common.logger.error(f"An error occurred while syncing the command tree: {e}")
                return await message.edit(content=""":no_entry:  **An error occurred while syncing the command tree**
See console for more information""")

            if log_channel:
                embed = discord.Embed(
                    title=None,
                    description=":deciduous_tree: **Global command tree synced**",
                    color=discord.Colour.greyple()
                )
                embed.timestamp = discord.utils.utcnow()

                await log_channel.send(embed=embed)
            
            await message.edit(content=":white_check_mark:  **COMMAND TREE SYNCED**")

    @commands.hybrid_command(name='ping', with_app_command=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def _ping(self, ctx):
        """Checks DEKKO's connection to the server"""

        async with ctx.typing():
            start = time.perf_counter()
            message = await ctx.send("Resolving...")
            end = time.perf_counter()
            
            duration = (end - start) * 1000

            embed = discord.Embed(
                title=None,
                description=":ping_pong: **Pong!**",
                color=discord.Colour.blurple()
            )
            embed.set_footer(text=f"Web socket latency: {round(self.bot.latency * 1000)}ms | Total latency: {duration:.0f}ms")

            message = await message.edit(content=None, embed=embed)

    @commands.hybrid_command(name='shutdown', with_app_command=True)
    @app_commands.allowed_installs(guilds=True, users=False)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @commands.is_owner()
    async def _shutdown(self, ctx):
        """Shuts down the bot"""

        async with ctx.typing():
            message = await ctx.send(":hourglass:  **DEKKO is shutting down...**")

            await message.edit(content=":electric_plug: **DEKKO is now offline**")
            await self.bot.close()

    @commands.hybrid_command(name='reboot', with_app_command=True)
    @app_commands.allowed_installs(guilds=True, users=False)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @commands.is_owner()
    async def _reboot(self, ctx):
        """Reboots DEKKO"""
        async with ctx.typing():
            await self.bot.change_presence(status=discord.Status.dnd, activity=discord.CustomActivity(name=f"DEKKO is rebooting..."))

            log_channel_id = await db.fetch_one("SELECT global_log_channel FROM global_config")
            log_channel = self.bot.get_channel(log_channel_id[0]) if log_channel_id else None

            message = await ctx.send(f":hourglass:  **Reboot <t:{int(time.time()) + 5}:R>**")
            time.sleep(4)

            if log_channel:
                embed = discord.Embed(
                    title=None,
                    description=f":electric_plug: **DEKKO was rebooted**",
                    color=discord.Colour.red()
                )
                embed.timestamp = discord.utils.utcnow()

                await log_channel.send(embed=embed)

            await message.edit(content=":electric_plug: **Rebooting...**")
            time.sleep(5)
            await self.bot.close()
            time.sleep(5)
            os.execl(sys.executable, sys.executable, *sys.argv)

async def setup(bot):
    await bot.add_cog(Core(bot))
