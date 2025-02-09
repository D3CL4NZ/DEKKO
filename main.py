import signal

import discord
from discord.ext import commands

import asyncio

import config

intents = discord.Intents.all()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix=commands.when_mentioned_or("$dekko "), intents=intents, activity=discord.CustomActivity(name=f"DEKKO! v{config.VERSION}"), status=discord.Status.online)

loop = asyncio.get_event_loop()

cog_files = [
    "commands.core",
    "commands.emoji_grabber",
    "commands.entropy",
    "commands.gulag",
    "commands.moderation",
    "commands.rmp",
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
    print("[DECCYLoader] Loading extensions...")
    for i in cog_files:
        await bot.load_extension(i)
        print("%s has loaded." % i)
    print("[DECCYLoader] All extensions have finished loading.")
    print("[DECCYLoader] Finished initialization. Logging in...")

async def main():
    async with bot:
        await load_extensions()
        await bot.start(config.TOKEN)

# Function to gracefully handle shutdown signal
def handle_shutdown():
    loop = asyncio.get_event_loop()
    loop.create_task(bot.close())
    print("Shutdown signal received. Closing bot...")

# Register signal handlers
signal.signal(signal.SIGINT, lambda sig, frame: handle_shutdown())
signal.signal(signal.SIGTERM, lambda sig, frame: handle_shutdown())

if __name__ == '__main__':
    loop.run_until_complete(main())
