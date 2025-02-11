import discord
from discord import app_commands
from discord.ext import commands

class ContextMenus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.reaction_info = app_commands.ContextMenu(
            name="Grab Reaction Emojis", callback=self._reaction_info
        )
        self.reaction_info_stealth = app_commands.ContextMenu(
            name="Grab Reaction Emojis (Stealth)", callback=self._reaction_info_stealth
        )
        self.bot.tree.add_command(self.reaction_info)
        self.bot.tree.add_command(self.reaction_info_stealth)

    async def cog_unload(self):
        self.bot.tree.remove_command(self.reaction_info.name, type=self.reaction_info.type)
        self.bot.tree.remove_command(self.reaction_info_stealth.name, type=self.reaction_info_stealth.type)

    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def _reaction_info(self, interaction: discord.Interaction, message: discord.Message):
        if not message.reactions:
            return await interaction.response.send_message(":no_entry:  **This message does not contain any reactions**", ephemeral=True)

        embedList = []
        for reaction in message.reactions:
            try:
                emoji = reaction.emoji
                if type(emoji) is str:
                    continue
                else:
                    emoji = await emoji.guild.fetch_emoji(emoji.id)
            except discord.NotFound:
                return await interaction.response.send_message(""":no_entry:  **An error has occured**```
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

            embedList.append(embed)

        if (len(embedList) <= 10):
            return await interaction.response.send_message(embeds=embedList, ephemeral=False)
        else:
            return await interaction.response.send_message(":no_entry:  **This message contains too many reactions**", ephemeral=True)

    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def _reaction_info_stealth(self, interaction: discord.Interaction, message: discord.Message):
        if not message.reactions:
            await interaction.response.send_message(":no_entry:  **This message does not contain any reactions**", ephemeral=True)

        embedList = []
        for reaction in message.reactions:
            try:
                emoji = reaction.emoji
                if type(emoji) is str:
                    continue
                else:
                    emoji = await emoji.guild.fetch_emoji(emoji.id)
            except discord.NotFound:
                await interaction.response.send_message(""":no_entry:  **An error has occured**```
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

            embedList.append(embed)

        if (len(embedList) <= 10):
            await interaction.response.send_message(embeds=embedList, ephemeral=True)
        else:
            await interaction.response.send_message(":no_entry:  **This message contains too many reactions**", ephemeral=True)


async def setup(bot):
    await bot.add_cog(ContextMenus(bot))
