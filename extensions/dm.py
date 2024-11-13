import discord
from discord import app_commands
from discord.ext import tasks, commands

import config

class DirectMessages(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("[Direct Messages] Hello :D")

    @commands.Cog.listener()
    async def on_message(self, message):
        if isinstance(message.channel, discord.channel.DMChannel) and message.author != self.bot.user:
            # Get attachments, if any
            attachments_string = "None"
            if message.attachments:
                attachment_urls = []
                for attachment in message.attachments:
                    attachment_urls.append(attachment.url)
                attachments_string = '\n'.join(attachment_urls)

            # Get message content
            content = "None"
            if message.content:
                content = message.content

            dm_channel = self.bot.get_channel(config.DM_CHANNEL_ID)
            embed = discord.Embed(title="DM Received", description=f":mailbox_with_mail: {message.author.mention} **sent you a DM!**", color=discord.Colour.blurple())
            embed.set_author(name=message.author.name, icon_url=message.author.display_avatar.url)
            embed.set_thumbnail(url=message.author.display_avatar.url)
            embed.add_field(name="Content", value=content, inline=False)
            embed.add_field(name="Attachments", value=attachments_string)
            embed.timestamp = discord.utils.utcnow()
            embed.set_footer(text=f"User ID: {message.author.id} | Message ID: {message.id}")
            await dm_channel.send(embed=embed)

    @commands.hybrid_command(name='dm', with_app_command=True)
    @app_commands.allowed_installs(guilds=True, users=False)
    @app_commands.allowed_contexts(guilds=True, dms=False, private_channels=True)
    @commands.has_any_role("supreme leader", "administrator", "moderator", "Supreme Leader", "Administrator", "Moderator")
    async def _dm(self, ctx, *, member: discord.Member, content):
        """Sends the specified user a DM"""
        try:
            embed = discord.Embed(title="DM Sent", description=f":incoming_envelope: **Sent DM to** {member.mention}", color=discord.Colour.blurple())
            embed.add_field(name="Content", value=content, inline=False)
            embed.timestamp = discord.utils.utcnow()
            embed.set_footer(text="User ID: {}".format(member.id))

            await member.send(content)
            await ctx.send(embed=embed)
        except:
            await ctx.send(f":mailbox_closed: **Message failed to send. {member.mention} has their DMs closed.**")

async def setup(bot):
        await bot.add_cog(DirectMessages(bot))
