import discord
from discord import app_commands
from discord.ext import commands

import common

class Whois(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='whois', with_app_command=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def _whois(self, ctx, user: discord.User):
        """Fetches information about a user"""

        async with ctx.typing():
            # Fetch the global user object, which includes the extended attributes
            # such as accent color, banner, etc.
            # This is necessary because the user object passed to the command
            # may not have all the attributes we want to display.
            user_object = await self.bot.fetch_user(user.id)

            creation_time = user_object.created_at.strftime("%I:%M %p %B %d, %Y")

            banner_url = f"[Link to Banner]({user_object.banner.url})" if hasattr(user_object.banner, 'url') else "`Not Available`"
            user_discriminator = '{:04}'.format(user_object.discriminator)
            mfa_enabled = user.mfa_enabled if hasattr(user, 'mfa_enabled') else "Unknown"
            is_verified = user.verified if hasattr(user, 'verified') else "Unknown"

            embed = discord.Embed(
                title=f"**User Information for:** `{user.display_name}`",
                description=None,
                color=user_object.accent_color
            )

            embed.set_author(name=user_object.name, icon_url=user_object.display_avatar.url)
            embed.set_thumbnail(url=user.display_avatar.url)

            embed.set_footer(text=f"DEKKO! v{common.VERSION}")
            embed.timestamp = discord.utils.utcnow()

            embed.add_field(name="__**General Attributes**__", value=f"""Username: `{user_object.name}`
Global Name: `{user_object.global_name}`
User ID: `{user_object.id}`
Color: `{user.color}`
Avatar URL: [Link to Avatar]({user_object.display_avatar.url})
Banner URL: {banner_url}
Account Created: `{creation_time}`""", inline=False)

            embed.add_field(name="__**Extended Attributes**__", value=f"""Mention: {user.mention}
Discriminator: `#{user_discriminator}`
Accent Color: `{user_object.accent_color}`
Default Avatar URL: [Link to Default Avatar]({user.default_avatar.url})
Is Bot: `{user_object.bot}`
Has 2FA Enabled: `{mfa_enabled}`
Has a Verified Email: `{is_verified}`""", inline=False)

            return await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Whois(bot))
