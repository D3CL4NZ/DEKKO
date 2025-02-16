import discord
from discord import app_commands
from discord.ext import commands

import traceback

import common
from webhook import DiscordWebhookSender
from database import db

class DeccyLoader(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        error_webhook_url = await db.fetch_one("SELECT error_webhook FROM logging_webhooks WHERE guild = ?", ctx.guild.id)
        error_webhook = DiscordWebhookSender(url=error_webhook_url[0]) if not(error_webhook_url is None or (isinstance(error_webhook_url, tuple) and all(url is None for url in error_webhook_url))) else None

        error = getattr(error, 'original', error)

        common.logger.error(''.join(traceback.format_exception(type(error), error, error.__traceback__)))
        await ctx.send(':no_entry:  **CYKA BLYAT!**\n`DECCYLoader` has encountered an error :( ```ansi\n{}```'.format(str(error)))
        if error_webhook:
            await error_webhook.send(':no_entry:  **CYKA BLYAT!**\n`DECCYLoader` has encountered an error :( ```ansi\n{}```'.format("".join(traceback.format_exception(type(error), error, error.__traceback__))))

    @commands.hybrid_group(invoke_without_command=True)
    @app_commands.allowed_installs(guilds=True, users=False)
    @app_commands.allowed_contexts(guilds=True, dms=False, private_channels=True)
    async def deccyloader(self, ctx):
        await ctx.send(':warning:  **You must specify a subcommand**')

    @deccyloader.command(name='load', with_app_command=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @commands.is_owner()
    async def _load(self, ctx, extension):
        """Loads an extension"""
        try:
            await self.bot.load_extension(extension)
            common.logger.info(f"[DECCYLoader]    -> {extension} has loaded.")
        except Exception as e:
            raise commands.ExtensionError(f"Failed to load extension {extension}") from e
        else:
            await ctx.send(f':white_check_mark:  **Successfully loaded extension `{extension}`**')

    @deccyloader.command(name='unload', with_app_command=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @commands.is_owner()
    async def _unload(self, ctx, extension):
        """Unloads an extension"""
        try:
            await self.bot.unload_extension(extension)
            common.logger.info(f"[DECCYLoader]    -> {extension} has unloaded.")
        except Exception as e:
            raise commands.ExtensionError(f"Failed to unload extension {extension}") from e
        else:
            await ctx.send(f':white_check_mark:  **Successfully unloaded extension `{extension}`**')

    @deccyloader.command(name='reload', with_app_command=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @commands.is_owner()
    async def _reload(self, ctx, extension):
        """Reloads an extension"""
        try:
            await self.bot.reload_extension(extension)
            common.logger.info(f"[DECCYLoader]    -> {extension} has reloaded.")
        except Exception as e:
            raise commands.ExtensionError(f"Failed to reload extension {extension}") from e
        else:
            await ctx.send(f':white_check_mark:  **Successfully reloaded extension `{extension}`**')

    @deccyloader.command(name='list', with_app_command=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @commands.is_owner()
    async def _list(self, ctx):
        """Lists all loaded extensions"""
        await ctx.send(f':white_check_mark:  **Loaded extensions:**\n```{", ".join(self.bot.extensions)}```')

async def setup(bot):
    await bot.add_cog(DeccyLoader(bot))
