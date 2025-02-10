from discord import app_commands
from discord.ext import commands

import time
import random

class Entropy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='coinflip', with_app_command=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def _status(self, ctx):
        """Flips a coin"""

        randomnum = random.randint(0,1)
        side = ""

        if(randomnum == 0):
            side = "heads"
        elif(randomnum == 1):
            side = "tails"
        else:
            side = "null"

        async with ctx.typing():
            message = await ctx.send(":hourglass: **Processing request...**")
            time.sleep(0.15)
            await message.edit(content=":radioactive: **Initializing geiger counter...**")
            time.sleep(0.15)
            await message.edit(content=":hourglass: **Gathering entropy for random seed...**")
            time.sleep(4)
            await message.edit(content=":coin: **Flipping coin...**")
            time.sleep(10)

            await message.edit(content=f"Coin landed on... **{side}**!")

async def setup(bot):
    await bot.add_cog(Entropy(bot))
