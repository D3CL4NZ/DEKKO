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
            user = await self.bot.fetch_user(user.id)

            creation_time = user.created_at.strftime("%I:%M %p %B %d, %Y")

            banner_url = f"[Link to Banner]({user.banner.url})" if hasattr(user.banner, 'url') else "`Not Available`"
            user_discriminator = '{:04}'.format(user.discriminator)
            mfa_enabled = user.mfa_enabled if hasattr(user, 'mfa_enabled') else "Unknown"
            is_verified = user.verified if hasattr(user, 'verified') else "Unknown"

            embed = discord.Embed(
                title=f"**User Information for:** `{user.display_name}`",
                description=None,
                color=user.accent_color
            )

            embed.set_author(name=user.name, icon_url=user.display_avatar.url)
            embed.set_thumbnail(url=user.display_avatar.url)

            embed.set_footer(text=f"DEKKO! v{common.VERSION}")
            embed.timestamp = discord.utils.utcnow()

            embed.add_field(name="__**General Attributes**__", value=f"""Username: `{user.name}`
Global Name: `{user.global_name}`
User ID: `{user.id}`
Color: `{user.color}`
Avatar URL: [Link to Avatar]({user.display_avatar.url})
Banner URL: {banner_url}
Account Created: `{creation_time}`""", inline=False)

            embed.add_field(name="__**Extended Attributes**__", value=f"""Mention: {user.mention}
Discriminator: `#{user_discriminator}`
Accent Color: `{user.accent_color}`
Default Avatar URL: [Link to Default Avatar]({user.default_avatar.url})
Is Bot: `{user.bot}`
Has 2FA Enabled: `{mfa_enabled}`
Has a Verified Email: `{is_verified}`""", inline=False)

            return await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Whois(bot))
