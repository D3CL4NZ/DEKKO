import discord
from discord import app_commands
from discord.ext import commands
import requests
import json
from expiringdict import ExpiringDict

import time

def error_message(error):
    if (error == 404):
        return discord.Embed(title="Definition not found", description="ERR_HTTP_CYKA_BLYAT_404_NOT_FOUND", color=discord.Colour.red())

def define_message(definition_block):
    # Word, Description, Word URL, Embed Color
    embed = discord.Embed(title=f"Definition of {definition_block['word']}",
                  description=definition_block["word_definition"], url=definition_block["permalink"], color=0x0b4ee7)

    # Embed Thumbnail
    embed.set_thumbnail(url="https://i.imgur.com/VFXr0ID.jpg?format=webp&width=563&height=563")

    # Add field for each example
    examples = ""
    embed.add_field(name="Example", value=definition_block["example"], inline=False)

    # Word ratings
    ratings = definition_block["ratings"]
    like_emoji = ":thumbsup:"
    dislike_emoji = ":thumbsdown:"
    embed.add_field(name=like_emoji, value=ratings[0], inline=True)
    embed.add_field(name=dislike_emoji, value=ratings[1], inline=True)

    # Word contributor (Author)
    embed.set_footer(text="Sent by {}".format(definition_block["contributor"]))
    return embed

def parse_and_scrape_definition(word):
    response = requests.get(f"https://api.urbandictionary.com/v0/define?term={word}")

    if response.status_code == 200:
        data = json.loads(response.text)

        if len(data["list"]) == 0:
            return {"error": 404}

        firstdef = data["list"][0] # Gets the first definition

        author = firstdef["author"]
        definition = firstdef["definition"]
        word = firstdef["word"]
        example = firstdef["example"]

        word_url = firstdef["permalink"]

        ratings = [firstdef["thumbs_up"], firstdef["thumbs_down"]]

        formatted_definition = dict()
        formatted_definition["word"] = word
        formatted_definition["permalink"] = word_url
        formatted_definition["word_definition"] = definition
        formatted_definition["contributor"] = author
        formatted_definition["example"] = example
        formatted_definition["ratings"] = ratings

        return formatted_definition

class Urban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # 3600 seconds (1 hour)
        self.cache = ExpiringDict(max_len=100, max_age_seconds=3600)

    @commands.hybrid_command(name='urban', with_app_command=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def _urban(self, ctx, *, search:str):
        """Search for a term on Urban Dictionary"""

        async with ctx.typing():
            # check if the word is cached
            word_definition = self.cache.get(f"{search}")

            if not word_definition:
                # scrape Word
                word_definition = parse_and_scrape_definition(search)

                # cache word
                self.cache["{}".format(search)] = word_definition

            if "error" in word_definition:
                embed = error_message(word_definition["error"])
                return await ctx.send(embed=embed)
            else:
                embed = define_message(word_definition)
                return await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Urban(bot))
