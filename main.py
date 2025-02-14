import discord
from discord.ext import commands

import asyncio
import signal

import config
import common

from database import db

intents = discord.Intents.all()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix=commands.when_mentioned_or("$dekko "), intents=intents, activity=discord.CustomActivity(name=f"DEKKO! v{common.VERSION}"), status=discord.Status.online)

loop = asyncio.get_event_loop()

cog_files = [
    "commands.core",
    "commands.emoji_grabber",
    "commands.entropy",
    "commands.gulag",
    "commands.moderation",
    "commands.rmp",
    "commands.setup_db",
    "commands.urban",
    "commands.verification",
    "commands.whois",
    "commands.ytdlp",
    "events",
    "extensions.context_menu",
    "extensions.dm",
    "extensions.holidays",
    "extensions.sus",
    "extensions.youtube"
]

async def load_extensions():
    common.logger.info("[DECCYLoader] Loading extensions...")
    for i in cog_files:
        await bot.load_extension(i)
        common.logger.info("[DECCYLoader]    -> %s has loaded." % i)
    common.logger.info("[DECCYLoader] All extensions have finished loading.")
    common.logger.info("[DECCYLoader] Finished initialization. Logging in...")

async def initialize_db():
    """Create the database if it doesn't exist"""

    await db.execute("""
        CREATE TABLE IF NOT EXISTS `global_config` (
            id INTEGER PRIMARY KEY,
            global_log_channel INTEGER,
            dm_channel INTEGER
        )
    """)

    await db.execute("""
        CREATE TABLE IF NOT EXISTS `config` (
            guild INTEGER PRIMARY KEY,
            log_channel INTEGER,
            error_channel INTEGER,
            admin_channel INTEGER,
            manver_channel INTEGER,
            exclude_logging_channels TEXT,
            owner_role_id INTEGER,
            admin_role_id INTEGER,
            mod_role_id INTEGER,
            bot_role_id INTEGER,
            human_role_id INTEGER,
            verified_role_id INTEGER,
            mute_role_id INTEGER,
            purgatory_role_id INTEGER,
            sus_role_id INTEGER
        )
    """)

    await db.execute("""
        CREATE TABLE IF NOT EXISTS `naughty_list` (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            reason TEXT
        )
    """)

    await db.execute("""
        CREATE TABLE IF NOT EXISTS `holidata` (
            guild INTEGER PRIMARY KEY,
            new_years_channel INTEGER,
            cn_new_years_channel INTEGER,
            vday_channel INTEGER,
            st_patricks_channel INTEGER,
            easter_channel INTEGER,
            cinco_de_mayo_channel INTEGER,
            j4_channel INTEGER,
            halloween_channel INTEGER,
            thanksgiving_channel INTEGER,
            christmas_channel INTEGER,
            wishlist_channel INTEGER
        )
    """)

    await db.execute("""
        CREATE TABLE IF NOT EXISTS `logging_webhooks` (
            guild INTEGER PRIMARY KEY,
            log_webhook TEXT,
            error_webhook TEXT
        )
    """)

    common.logger.info("[DECCYLoader] Database initialized.")

async def main():
    await db.connect() # Initialize the database
    await initialize_db() # Create the database if it doesn't exist

    async with bot:
        await load_extensions() # Load extensions
        await bot.start(config.TOKEN)

# Function to gracefully handle shutdown signal
def handle_shutdown():
    loop.call_soon_threadsafe(asyncio.create_task, bot.close())
    loop.call_soon_threadsafe(asyncio.create_task, db.close())
    common.logger.warning("[DECCYLoader] Shutdown signal received. Closing bot...")

# Register signal handlers
signal.signal(signal.SIGINT, lambda sig, frame: handle_shutdown())
signal.signal(signal.SIGTERM, lambda sig, frame: handle_shutdown())

if __name__ == '__main__':
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(bot.close())
        loop.run_until_complete(db.close())
        loop.close()
