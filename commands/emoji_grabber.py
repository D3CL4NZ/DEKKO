import discord
from discord import app_commands
from discord.ext import commands

class EmojiGrabber(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='grabreactions', with_app_command=True)
    @app_commands.allowed_installs(guilds=True, users=False)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def _grab_reaction(self, ctx, message: discord.Message):
        """Grabs all reactions from a message"""

        if not message.reactions:
            return await ctx.send(":no_entry:  **This message does not contain any reactions**", ephemeral=True)

        embedList = []
        for reaction in message.reactions:
            try:
                emoji = reaction.emoji
                if type(emoji) is str:
                    continue
                else:
                    emoji = await emoji.guild.fetch_emoji(emoji.id)
            except discord.NotFound:
                return await ctx.send(""":no_entry:  **An error has occured**```
See the log for more details.```""", ephemeral=True)
            except:
                pass

            is_managed = emoji.managed if type(emoji) is discord.Emoji else "`Not available`"
            is_animated = True if emoji.animated else False
            requires_colons = emoji.require_colons if type(emoji) is discord.Emoji else "`Not available`"
            creation_time = emoji.created_at.strftime("%I:%M %p %B %d, %Y")
            emoji_author = emoji.user.mention if type(emoji) is discord.Emoji else "`Not available`"

            can_use_emoji = "`Not available`"
            if type(emoji) is discord.Emoji:
                can_use_emoji = "@everyone" if not emoji.roles else " ".join(role.mention for role in emoji.roles)

            emoji_guild_name = emoji.guild.name if type(emoji) is discord.Emoji else "`Not available`"
            emoji_guild_id = emoji.guild.id if type(emoji) is discord.Emoji else "`Not available`"

            embed = discord.Embed(
                title=f"**Emoji Information for:** `{emoji.name}`",
                description=None,
                color=0xadd8e6
            )

            embed.set_thumbnail(url=emoji.url)

            embed.add_field(name="__**General**__", value=f"""Name: `{emoji.name}`
ID: `{emoji.id}`
URL: [Link to Emoji]({emoji.url})
Author: {emoji_author}
Time Created: `{creation_time}`
Usable by: {can_use_emoji}""", inline=False)

            embed.add_field(name="__**Other**__", value=f"""Animated: `{is_animated}`
Managed: `{is_managed}`
Requires Colons: `{requires_colons}`
Guild Name: `{emoji_guild_name}`
Guild ID: `{emoji_guild_id}`""", inline=False)

            embed.set_footer(text="Made with <3 by D3CL4NZ")

            embedList.append(embed)

        if (len(embedList) <= 10):
            return await ctx.send(embeds=embedList, ephemeral=False)
        else:
            return await ctx.send(":no_entry:  **This message contains too many reactions**", ephemeral=True)

    @commands.hybrid_command(name='grabreactions-stealth', with_app_command=True)
    @app_commands.allowed_installs(guilds=True, users=False)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def _grab_reaction_stealth(self, ctx, message: discord.Message):
        """Grabs all reactions from a message (quietly)"""

        if not message.reactions:
            await ctx.send(":no_entry:  **This message does not contain any reactions**", ephemeral=True)

        embedList = []
        for reaction in message.reactions:
            try:
                emoji = reaction.emoji
                if type(emoji) is str:
                    continue
                else:
                    emoji = await emoji.guild.fetch_emoji(emoji.id)
            except discord.NotFound:
                await ctx.send(""":no_entry:  **An error has occured**```
See the log for more details.```""", ephemeral=True)
            except:
                pass

            is_managed = emoji.managed if type(emoji) is discord.Emoji else "`Not available`"
            is_animated = True if emoji.animated else False
            requires_colons = emoji.require_colons if type(emoji) is discord.Emoji else "`Not available`"
            creation_time = emoji.created_at.strftime("%I:%M %p %B %d, %Y")
            emoji_author = emoji.user.mention if type(emoji) is discord.Emoji else "`Not available`"

            can_use_emoji = "`Not available`"
            if type(emoji) is discord.Emoji:
                can_use_emoji = "@everyone" if not emoji.roles else " ".join(role.mention for role in emoji.roles)

            emoji_guild_name = emoji.guild.name if type(emoji) is discord.Emoji else "`Not available`"
            emoji_guild_id = emoji.guild.id if type(emoji) is discord.Emoji else "`Not available`"

            embed = discord.Embed(
                title=f"**Emoji Information for:** `{emoji.name}`",
                description=None,
                color=0xadd8e6
            )

            embed.set_thumbnail(url=emoji.url)

            embed.add_field(name="__**General**__", value=f"""Name: `{emoji.name}`
ID: `{emoji.id}`
URL: [Link to Emoji]({emoji.url})
Author: {emoji_author}
Time Created: `{creation_time}`
Usable by: {can_use_emoji}""", inline=False)

            embed.add_field(name="__**Other**__", value=f"""Animated: `{is_animated}`
Managed: `{is_managed}`
Requires Colons: `{requires_colons}`
Guild Name: `{emoji_guild_name}`
Guild ID: `{emoji_guild_id}`""", inline=False)

            embed.set_footer(text="Made with <3 by D3CL4NZ")

            embedList.append(embed)

        if (len(embedList) <= 10):
            await ctx.send(embeds=embedList, ephemeral=True)
        else:
            await ctx.send(":no_entry:  **This message contains too many reactions**", ephemeral=True)


async def setup(bot):
    await bot.add_cog(EmojiGrabber(bot))
