import sys
import signal

import discord
from discord.ext import commands

import asyncio

import config

intents = discord.Intents.all()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix=commands.when_mentioned_or("$dekko "), intents=intents, activity=discord.CustomActivity(name=f"DEKKO! v{config.VERSION}"), status=discord.Status.online)

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

def signal_handler(sig, frame):
    print('Shutting down...')
    asyncio.get_event_loop().run_until_complete(bot.close())

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
