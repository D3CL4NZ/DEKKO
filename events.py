import discord
from discord.ext import commands

from typing import Union

import traceback

from webhook import DiscordWebhookSender

import common

from database import db

class Events(commands.Cog):
    def __init__(self, bot):
        common.logger.info("[DECCYLoader] Initializing events and logging...")
        self.bot = bot

    # ============
    #  Member Log
    # ============

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        log_webhook_url = await db.fetch_one("SELECT log_webhook FROM logging_webhooks WHERE guild = ?", member.guild.id)
        log_webhook = DiscordWebhookSender(url=log_webhook_url[0]) if not(log_webhook_url is None or (isinstance(log_webhook_url, tuple) and all(url is None for url in log_webhook_url))) else None

        bot_role_id = await db.fetch_one("SELECT bot_role_id FROM config WHERE guild = ?", member.guild.id)
        bot_role = member.guild.get_role(bot_role_id[0]) if bot_role_id else None

        if log_webhook:
            embed = discord.Embed(
                title=None,
                description=f":tada: {member.mention} **joined the server**",
                color=discord.Colour.green()
            )
            embed.set_author(name=member.name, icon_url=member.display_avatar.url)
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.add_field(name="Account creation date", value=member.created_at.strftime("%I:%M %p %B %d, %Y"), inline=False)
            embed.timestamp = discord.utils.utcnow()
            embed.set_footer(text=f"User ID: {member.id}")

            await log_webhook.send(embed=embed)

        if bot_role:
            if member.bot:
                await member.add_roles(bot_role)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        log_webhook_url = await db.fetch_one("SELECT log_webhook FROM logging_webhooks WHERE guild = ?", member.guild.id)
        log_webhook = DiscordWebhookSender(url=log_webhook_url[0]) if not(log_webhook_url is None or (isinstance(log_webhook_url, tuple) and all(url is None for url in log_webhook_url))) else None

        general_channel = member.guild.system_channel

        if log_webhook:
            roles = []

            for i in range(1, len(member.roles)):
                    roles.append(member.roles[i].mention)

            embed = discord.Embed(
                title=None,
                description=f":dash: {member.mention} **left the server**",
                color=discord.Colour.red()
            )
            embed.set_author(name=member.name, icon_url=member.display_avatar.url)
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.add_field(name="Join date", value=member.joined_at.strftime("%I:%M %p %B %d, %Y"), inline=False)
            embed.add_field(name="Roles", value=' '.join(roles), inline=False)
            embed.timestamp = discord.utils.utcnow()
            embed.set_footer(text=f"User ID: {member.id}")

            await log_webhook.send(embed=embed)

        await general_channel.send(f"{member.mention} **left the server :(**", allowed_mentions=discord.AllowedMentions(users=False, everyone=False, roles=False, replied_user=False))

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        log_webhook_url = await db.fetch_one("SELECT log_webhook FROM logging_webhooks WHERE guild = ?", after.guild.id)
        log_webhook = DiscordWebhookSender(url=log_webhook_url[0]) if not(log_webhook_url is None or (isinstance(log_webhook_url, tuple) and all(url is None for url in log_webhook_url))) else None

        if log_webhook:
            to_send = False
            embed_list = []

            if before.display_avatar != after.display_avatar:
                to_send = True

                embed = discord.Embed(
                    title=None,
                    description=f"{before.mention} **updated their profile!**",
                    color=0xfaa41b
                )
                embed.set_author(name=before.name, icon_url=before.display_avatar.url)
                embed.set_thumbnail(url=after.display_avatar.url)
                embed.add_field(name="Guild avatar", value=f"[[before]]({before.display_avatar.url}) -> [[after]]({after.display_avatar.url})", inline=False)
                embed.timestamp = discord.utils.utcnow()
                embed.set_footer(text=f"User ID: {before.id}")

                embed_list.append(embed)

            if before.nick != after.nick:
                to_send = True

                embed = discord.Embed(
                    title=None,
                    description=f":pencil: {before.mention} **nickname edited**",
                    color=0xfaa41b
                )
                embed.set_author(name=before.name, icon_url=after.display_avatar.url)
                embed.set_thumbnail(url=after.display_avatar.url)
                embed.add_field(name="Old nickname", value=f"`{before.nick}`", inline=True)
                embed.add_field(name="New nickname", value=f"`{after.nick}`", inline=True)
                embed.timestamp = discord.utils.utcnow()
                embed.set_footer(text=f"User ID: {before.id}")

                embed_list.append(embed)

            if before.roles != after.roles:
                to_send = True

                added_roles = [x for x in after.roles if x not in before.roles]
                removed_roles = [x for x in before.roles if x not in after.roles]

                if added_roles:
                    if removed_roles:
                        embed = discord.Embed(
                            title=None,
                            description=f":crossed_swords: {before.mention} **roles have changed**",
                            color=0xfaa41b
                        )
                        embed.set_author(name=before.name, icon_url=after.display_avatar.url)
                        embed.set_thumbnail(url=after.display_avatar.url)
                        embed.add_field(name=":white_check_mark: Added roles", value=' '.join([x.mention for x in added_roles]), inline=False)
                        embed.add_field(name=":no_entry: Removed roles", value=' '.join([x.mention for x in removed_roles]), inline=False)
                        embed.timestamp = discord.utils.utcnow()
                        embed.set_footer(text=f"User ID: {before.id}")

                        embed_list.append(embed)
                    else:
                        embed = discord.Embed(
                            title=None,
                            description=f":crossed_swords: {before.mention} **roles have changed**",
                            color=0xfaa41b
                        )
                        embed.set_author(name=before.name, icon_url=after.display_avatar.url)
                        embed.set_thumbnail(url=after.display_avatar.url)
                        embed.add_field(name=":white_check_mark: Added roles", value=' '.join([x.mention for x in added_roles]), inline=False)
                        embed.timestamp = discord.utils.utcnow()
                        embed.set_footer(text=f"User ID: {before.id}")

                        embed_list.append(embed)
                elif removed_roles:
                    embed = discord.Embed(
                        title=None,
                        description=f":crossed_swords: {before.mention} **roles have changed**",
                        color=0xfaa41b
                    )
                    embed.set_author(name=before.name, icon_url=after.display_avatar.url)
                    embed.set_thumbnail(url=after.display_avatar.url)
                    embed.add_field(name=":no_entry: Removed roles", value=' '.join([x.mention for x in removed_roles]), inline=False)
                    embed.timestamp = discord.utils.utcnow()
                    embed.set_footer(text=f"User ID: {before.id}")

                    embed_list.append(embed)

            if to_send:
                await log_webhook.send(embeds=embed_list)

    @commands.Cog.listener()
    async def on_user_update(self, before: discord.User, after: discord.User):
        for guild in after.mutual_guilds:
            log_webhook_url = await db.fetch_one("SELECT log_webhook FROM logging_webhooks WHERE guild = ?", guild.id)
            log_webhook = DiscordWebhookSender(url=log_webhook_url[0]) if not(log_webhook_url is None or (isinstance(log_webhook_url, tuple) and all(url is None for url in log_webhook_url))) else None

            if log_webhook:
                to_send = False
                embed_list = []

                if before.display_avatar != after.display_avatar:
                    to_send = True

                    embed = discord.Embed(
                        title=None,
                        description=f"{before.mention} **updated their profile!**",
                        color=0xfaa41b
                    )
                    embed.set_author(name=before.name, icon_url=before.display_avatar.url)
                    embed.set_thumbnail(url=after.display_avatar.url)
                    embed.add_field(name="Avatar", value=f"[[before]]({before.display_avatar.url}) -> [[after]]({after.display_avatar.url})", inline=False)
                    embed.timestamp = discord.utils.utcnow()
                    embed.set_footer(text=f"User ID: {before.id}")

                    embed_list.append(embed)

                if before.global_name != after.global_name:
                    to_send = True

                    embed = discord.Embed(
                        title=None,
                        description=f"{before.mention} **updated their profile!**",
                        color=0xfaa41b
                    )
                    embed.set_author(name=before.name, icon_url=after.display_avatar.url)
                    embed.set_thumbnail(url=after.display_avatar.url)
                    embed.add_field(name="Global name", value=f"{before.global_name} -> {after.global_name}", inline=False)
                    embed.timestamp = discord.utils.utcnow()
                    embed.set_footer(text=f"User ID: {before.id}")

                    embed_list.append(embed)

                if before.name != after.name:
                    to_send = True

                    embed = discord.Embed(
                        title=None,
                        description=f"{before.mention} **updated their profile!**",
                        color=0xfaa41b
                    )
                    embed.set_author(name=before.name, icon_url=after.display_avatar.url)
                    embed.set_thumbnail(url=after.display_avatar.url)
                    embed.add_field(name="Username", value=f"{before.name} -> {after.name}", inline=False)
                    embed.timestamp = discord.utils.utcnow()
                    embed.set_footer(text=f"User ID: {before.id}")

                    embed_list.append(embed)

                if before.discriminator != after.discriminator:
                    to_send = True

                    before_discriminator = '{:04}'.format(before.discriminator)
                    after_discriminator = '{:04}'.format(after.discriminator)

                    embed = discord.Embed(
                        title=None,
                        description=f"{before.mention} **updated their profile!**",
                        color=0xfaa41b
                    )
                    embed.set_author(name=after.name, icon_url=after.display_avatar.url)
                    embed.set_thumbnail(url=after.display_avatar.url)
                    embed.add_field(name="Discriminator", value=f"#{before_discriminator} -> #{after_discriminator}", inline=False)
                    embed.timestamp = discord.utils.utcnow()
                    embed.set_footer(text=f"User ID: {before.id}")

                    embed_list.append(embed)

                if to_send:
                    await log_webhook.send(embeds=embed_list)

    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: Union[discord.User, discord.Member]):
        log_webhook_url = await db.fetch_one("SELECT log_webhook FROM logging_webhooks WHERE guild = ?", guild.id)
        log_webhook = DiscordWebhookSender(url=log_webhook_url[0]) if not(log_webhook_url is None or (isinstance(log_webhook_url, tuple) and all(url is None for url in log_webhook_url))) else None

        if log_webhook:
            embed = discord.Embed(
                title=None,
                description=f":man_police_officer: :lock: {user.mention} **was banned**",
                color=discord.Colour.red()
            )
            embed.set_author(name=user.name, icon_url=user.display_avatar.url)
            embed.set_thumbnail(url=user.display_avatar.url)
            embed.timestamp = discord.utils.utcnow()
            embed.set_footer(text=f"User ID: {user.id}")

            await log_webhook.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, user: Union[discord.User, discord.Member]):
        log_webhook_url = await db.fetch_one("SELECT log_webhook FROM logging_webhooks WHERE guild = ?", guild.id)
        log_webhook = DiscordWebhookSender(url=log_webhook_url[0]) if not(log_webhook_url is None or (isinstance(log_webhook_url, tuple) and all(url is None for url in log_webhook_url))) else None

        if log_webhook:
            embed = discord.Embed(
                title=None,
                description=f":man_police_officer: :unlock: {user.mention} **was unbanned**",
                color=discord.Colour.green()
            )
            embed.set_author(name=user.name, icon_url=user.display_avatar.url)
            embed.set_thumbnail(url=user.display_avatar.url)
            embed.timestamp = discord.utils.utcnow()
            embed.set_footer(text=f"User ID: {user.id}")

            await log_webhook.send(embed=embed)

    # ============
    #  Server Log
    # ============

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel):
        log_webhook_url = await db.fetch_one("SELECT log_webhook FROM logging_webhooks WHERE guild = ?", channel.guild.id)
        log_webhook = DiscordWebhookSender(url=log_webhook_url[0]) if not(log_webhook_url is None or (isinstance(log_webhook_url, tuple) and all(url is None for url in log_webhook_url))) else None
        
        if log_webhook:
            # Determine channel type
            channel_type = (
                "Text channel" if isinstance(channel, discord.TextChannel) else
                "Voice channel" if isinstance(channel, discord.VoiceChannel) else
                "Category" if isinstance(channel, discord.CategoryChannel) else
                "Stage channel" if isinstance(channel, discord.StageChannel) else
                "Forum channel" if isinstance(channel, discord.ForumChannel) else
                "Channel"
            )

            embed = discord.Embed(
                    title=None,
                    description=f":new: **{channel_type} created: #{channel.name}**",
                    color=discord.Colour.green()
                )
            embed.timestamp = discord.utils.utcnow()
            embed.set_footer(text=f"Channel ID: {channel.id}")

            await log_webhook.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        log_webhook_url = await db.fetch_one("SELECT log_webhook FROM logging_webhooks WHERE guild = ?", channel.guild.id)
        log_webhook = DiscordWebhookSender(url=log_webhook_url[0]) if not(log_webhook_url is None or (isinstance(log_webhook_url, tuple) and all(url is None for url in log_webhook_url))) else None
        
        if log_webhook:
            # Determine channel type
            channel_type = (
                "Text channel" if isinstance(channel, discord.TextChannel) else
                "Voice channel" if isinstance(channel, discord.VoiceChannel) else
                "Category" if isinstance(channel, discord.CategoryChannel) else
                "Stage channel" if isinstance(channel, discord.StageChannel) else
                "Forum channel" if isinstance(channel, discord.ForumChannel) else
                "Channel"
            )
                
            embed = discord.Embed(
                    title=None,
                    description=f":wastebasket: **{channel_type} deleted: #{channel.name}**",
                    color=discord.Colour.red()
                )
            embed.timestamp = discord.utils.utcnow()
            embed.set_footer(text=f"Channel ID: {channel.id}")

            await log_webhook.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before: discord.abc.GuildChannel, after: discord.abc.GuildChannel):
        # Don't log channels that are excluded
        excluded_channels = await db.fetch_one("SELECT exclude_logging_channels FROM config WHERE guild = ?", after.guild.id)
        if excluded_channels:
            excluded_channels = excluded_channels[0].split(',')

        if before.id in excluded_channels:
            return

        log_webhook_url = await db.fetch_one("SELECT log_webhook FROM logging_webhooks WHERE guild = ?", after.guild.id)
        log_webhook = DiscordWebhookSender(url=log_webhook_url[0]) if not(log_webhook_url is None or (isinstance(log_webhook_url, tuple) and all(url is None for url in log_webhook_url))) else None

        if log_webhook:
            embed_list = []

            # Determine channel type
            channel_type = (
                "Text channel" if isinstance(before, discord.TextChannel) else
                "Voice channel" if isinstance(before, discord.VoiceChannel) else
                "Category" if isinstance(before, discord.CategoryChannel) else
                "Stage channel" if isinstance(before, discord.StageChannel) else
                "Forum channel" if isinstance(before, discord.ForumChannel) else
                "Channel"
            )

            if before.overwrites != after.overwrites:
                # Getting the differences between the old and new overwrites
                added_overwrites = {key: after.overwrites[key] for key in after.overwrites if key not in before.overwrites}
                removed_overwrites = {key: before.overwrites[key] for key in before.overwrites if key not in after.overwrites}
                changed_overwrites = {key: after.overwrites[key] for key in after.overwrites if key in before.overwrites and before.overwrites[key] != after.overwrites[key]}

                def list_neutralized_permissions(before_overwrite: discord.PermissionOverwrite, after_overwrite: discord.PermissionOverwrite):
                    """Get permissions neutralized in the update."""
                    neutralized_permissions = []
                    for perm in dir(before_overwrite):
                        if not perm.startswith('__') and not callable(getattr(before_overwrite, perm)):
                            before_value = getattr(before_overwrite, perm)
                            after_value = getattr(after_overwrite, perm)
                            if before_value is not None and after_value is None:  # Check if the permission was neutralized
                                neutralized_permissions.append(perm.replace("_"," "))
                    return neutralized_permissions

                # Handle added overwrites
                for target, overwrite in added_overwrites.items():
                    allow, deny = overwrite.pair()
                    allowed_perms = [perm.replace("_", " ") for perm, value in allow if value]
                    denied_perms = [perm.replace("_", " ") for perm, value in deny if value]

                    embed = discord.Embed(
                        description=f":crossed_swords: **Channel permissions updated:** {before.mention}\nAdded permissions for: `{target.name}`",
                        color=discord.Colour.green(),
                    )
                    embed.add_field(name="\u2713 Allowed permissions", value=', '.join(allowed_perms) if allow else "None", inline=False)
                    embed.add_field(name="\u2718 Denied permissions", value=', '.join(denied_perms) if deny else "None", inline=False)
                    embed.timestamp = discord.utils.utcnow()
                    embed.set_footer(text=f"Channel ID: {before.id}")
                    embed_list.append(embed)

                # Handle removed overwrites
                for target, overwrite in removed_overwrites.items():
                    allow, deny = overwrite.pair()
                    allowed_perms = [perm.replace("_", " ") for perm, value in allow if value]
                    denied_perms = [perm.replace("_", " ") for perm, value in deny if value]

                    embed = discord.Embed(
                        description=f":crossed_swords: **Channel permissions updated:** {before.mention}\nRemoved permissions for: `{target.name}`",
                        color=discord.Colour.red(),
                    )
                    embed.add_field(name="\u2713 Allowed permissions", value=', '.join(allowed_perms) if allow else "None", inline=False)
                    embed.add_field(name="\u2718 Denied permissions", value=', '.join(denied_perms) if deny else "None", inline=False)
                    embed.timestamp = discord.utils.utcnow()
                    embed.set_footer(text=f"Channel ID: {before.id}")
                    embed_list.append(embed)

                # Handle changed overwrites
                for target, overwrite in changed_overwrites.items():
                    allow, deny = overwrite.pair()
                    allowed_perms = [perm.replace("_", " ") for perm, value in allow if value]
                    denied_perms = [perm.replace("_", " ") for perm, value in deny if value]
                    neutral_perms = list_neutralized_permissions(before.overwrites[target], overwrite)

                    embed = discord.Embed(
                        description=f":crossed_swords: **Channel permissions updated:** {before.mention}\nEdited permissions for: `{target.name}`",
                        color=0xfaa41b,
                    )
                    if allowed_perms:
                        embed.add_field(name="\u2713 Allowed permissions", value=', '.join(allowed_perms), inline=False)
                    if denied_perms:
                        embed.add_field(name="\u2718 Denied permissions", value=', '.join(denied_perms), inline=False)
                    if neutral_perms:
                        embed.add_field(name="\u29c4 Neutral permissions", value=', '.join(neutral_perms), inline=False)
                    
                    embed.timestamp = discord.utils.utcnow()
                    embed.set_footer(text=f"Channel ID: {before.id}")
                    embed_list.append(embed)

            # Log everything else

            if before.name != after.name:
                embed = discord.Embed(
                    title=None,
                    description=f":pencil: **{channel_type} updated: {before.name}**",
                    color=0xfaa41b
                )
                embed.add_field(name="Renamed", value=f"{before.name} -> {after.name}", inline=False)
                embed.timestamp = discord.utils.utcnow()
                embed.set_footer(text=f"Channel ID: {before.id}")

                embed_list.append(embed)

            if hasattr(before, "nsfw"):
                if before.is_nsfw() != after.is_nsfw():
                    embed = discord.Embed(
                        title=None,
                        description=f":pencil: **{channel_type} updated: {before.name}**",
                        color=0xfaa41b
                    )
                    embed.add_field(name="NSFW", value=f"{'Yes' if before.is_nsfw() else 'No'} -> {'Yes' if after.is_nsfw() else 'No'}", inline=False)
                    embed.timestamp = discord.utils.utcnow()
                    embed.set_footer(text=f"Channel ID: {before.id}")

                    embed_list.append(embed)

            if hasattr(before, "slowmode_delay"):
                if before.slowmode_delay != after.slowmode_delay:
                    if before.slowmode_delay == 0:
                        embed = discord.Embed(
                            title=None,
                            description=f":pencil: **{channel_type} updated: {before.name}**",
                            color=0xfaa41b
                        )
                        embed.add_field(name="Slowmode", value=f"Off -> {after.slowmode_delay}", inline=False)
                        embed.timestamp = discord.utils.utcnow()
                        embed.set_footer(text=f"Channel ID: {before.id}")
                    elif after.slowmode_delay == 0:
                        embed = discord.Embed(
                            title=None,
                            description=f":pencil: **{channel_type} updated: {before.name}**",
                            color=0xfaa41b
                        )
                        embed.add_field(name="Slowmode", value=f"{before.slowmode_delay} -> Off", inline=False)
                        embed.timestamp = discord.utils.utcnow()
                        embed.set_footer(text=f"Channel ID: {before.id}")
                    else:
                        embed = discord.Embed(
                            title=None,
                            description=f":pencil: **{channel_type} updated: {before.name}**",
                            color=0xfaa41b
                        )
                        embed.add_field(name="Slowmode", value=f"{before.slowmode_delay} -> {after.slowmode_delay}", inline=False)
                        embed.timestamp = discord.utils.utcnow()
                        embed.set_footer(text=f"Channel ID: {before.id}")

                    embed_list.append(embed)

            if hasattr(before, "topic"):
                if before.topic != after.topic:
                    embed = discord.Embed(
                        title=None,
                        description=f":pencil: **{channel_type} updated: {before.name}**",
                        color=0xfaa41b
                    )
                    embed.add_field(name="Topic", value=f"{before.topic} -> {after.topic}", inline=False)
                    embed.timestamp = discord.utils.utcnow()
                    embed.set_footer(text=f"Channel ID: {before.id}")

                    embed_list.append(embed)

            if hasattr(before, "bitrate"):
                if before.bitrate != after.bitrate:
                    embed = discord.Embed(
                        title=None,
                        description=f":pencil: **{channel_type} updated: {before.name}**",
                        color=0xfaa41b
                    )
                    embed.add_field(name="Bitrate", value=f"{before.bitrate} -> {after.bitrate}", inline=False)
                    embed.timestamp = discord.utils.utcnow()
                    embed.set_footer(text=f"Channel ID: {before.id}")

                    embed_list.append(embed)

            if hasattr(before, "rtc_region"):
                if before.rtc_region != after.rtc_region:
                    embed = discord.Embed(
                        title=None,
                        description=f":pencil: **{channel_type} updated: {before.name}**",
                        color=0xfaa41b
                    )
                    embed.add_field(name="RTC Region", value=f"{before.rtc_region} -> {after.rtc_region}", inline=False)
                    embed.timestamp = discord.utils.utcnow()
                    embed.set_footer(text=f"Channel ID: {before.id}")

                    embed_list.append(embed)

            if hasattr(before, "user_limit"):
                if before.user_limit != after.user_limit:
                    embed = discord.Embed(
                        title=None,
                        description=f":pencil: **{channel_type} updated: {before.name}**",
                        color=0xfaa41b
                    )
                    embed.add_field(name="User limit", value=f"{before.user_limit} -> {after.user_limit}", inline=False)
                    embed.timestamp = discord.utils.utcnow()
                    embed.set_footer(text=f"Channel ID: {before.id}")

                    embed_list.append(embed)

            if embed_list:
                for i in range(0, len(embed_list), 10):
                    chunk = embed_list[i:i + 10]
                    await log_webhook.send(embeds=chunk)

    @commands.Cog.listener()
    async def on_guild_role_create(self, role: discord.Role):
        log_webhook_url = await db.fetch_one("SELECT log_webhook FROM logging_webhooks WHERE guild = ?", role.guild.id)
        log_webhook = DiscordWebhookSender(url=log_webhook_url[0]) if not(log_webhook_url is None or (isinstance(log_webhook_url, tuple) and all(url is None for url in log_webhook_url))) else None

        if log_webhook:
            perms_list = [perm[0].replace("_", " ") for perm in role.permissions if perm[1]]

            embed = discord.Embed(
                title=None,
                description=f":crossed_swords: **Role created: {role.name}**",
                color=discord.Colour.green()
            )
            embed.add_field(name="Permissions", value=", ".join(perms_list) if perms_list else "none", inline=False)
            embed.timestamp = discord.utils.utcnow()
            embed.set_footer(text=f"Role ID: {role.id}")

            await log_webhook.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role):
        log_webhook_url = await db.fetch_one("SELECT log_webhook FROM logging_webhooks WHERE guild = ?", role.guild.id)
        log_webhook = DiscordWebhookSender(url=log_webhook_url[0]) if not(log_webhook_url is None or (isinstance(log_webhook_url, tuple) and all(url is None for url in log_webhook_url))) else None

        if log_webhook:
            perms_list = [perm[0].replace("_", " ") for perm in role.permissions if perm[1]]

            embed = discord.Embed(
                title=None,
                description=f":wastebasket: **Role deleted: {role.name}**",
                color=discord.Colour.red()
            )
            embed.add_field(name="Color", value=role.color, inline=True)
            embed.add_field(name="Hoisted", value="Yes" if role.hoist else "No", inline=True)
            embed.add_field(name="Mentionable", value="Yes" if role.mentionable else "No", inline=True)
            if perms_list:
                embed.add_field(name="Permissions", value=", ".join(perms_list), inline=False)
            embed.timestamp = discord.utils.utcnow()
            embed.set_footer(text=f"Role ID: {role.id}")

            await log_webhook.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_role_update(self, before: discord.Role, after: discord.Role):
        log_webhook_url = await db.fetch_one("SELECT log_webhook FROM logging_webhooks WHERE guild = ?", after.guild.id)
        log_webhook = DiscordWebhookSender(url=log_webhook_url[0]) if not(log_webhook_url is None or (isinstance(log_webhook_url, tuple) and all(url is None for url in log_webhook_url))) else None

        if log_webhook:
            embed = discord.Embed(
                title=None,
                description=f":pencil: **Role updated: {before.name}**",
                color=0xfaa41b
            )

            if before.color != after.color:
                embed.add_field(name="Color", value=f"{before.color} -> {after.color}", inline=False)

            if before.name != after.name:
                embed.add_field(name="Name", value=f"{before.name} -> {after.name}", inline=False)
            
            if before.hoist != after.hoist:
                embed.add_field(name="Hoisted", value=f"{'Yes' if before.hoist else 'No'} -> {'Yes' if after.hoist else 'No'}", inline=False)

            if before.mentionable != after.mentionable:
                embed.add_field(name="Mentionable", value=f"{'Yes' if before.mentionable else 'No'} -> {'Yes' if after.mentionable else 'No'}", inline=False)
            
            if before.permissions != after.permissions:
                allowed_permissions = []
                denied_permissions = []

                for perm, value in before.permissions:
                    after_value = dict(after.permissions)[perm]

                    if value != after_value:
                        allowed_permissions.append(perm.replace("_", " ")) if after_value else denied_permissions.append(perm.replace("_", " "))

                if allowed_permissions:
                    embed.add_field(name="\u2713 Allowed permissions", value=", ".join(allowed_permissions), inline=False)
                
                if denied_permissions:
                    embed.add_field(name="\u2718 Denied permissions", value=", ".join(denied_permissions), inline=False)

            embed.timestamp = discord.utils.utcnow()
            embed.set_footer(text=f"Role ID: {before.id}")

            await log_webhook.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_update(self, before: discord.Guild, after: discord.Guild):
        log_webhook_url = await db.fetch_one("SELECT log_webhook FROM logging_webhooks WHERE guild = ?", after.guild.id)
        log_webhook = DiscordWebhookSender(url=log_webhook_url[0]) if not(log_webhook_url is None or (isinstance(log_webhook_url, tuple) and all(url is None for url in log_webhook_url))) else None

        if log_webhook:
            embed = discord.Embed(
                title=None,
                description=f":pencil: **Server information updated!**",
                color=0xfaa41b
            )

            if before.afk_channel != after.afk_channel:
                embed.add_field(name="AFK channel", value=f"{before.afk_channel.mention} -> {after.afk_channel.mention}", inline=False)
            
            if before.afk_timeout != after.afk_timeout:
                embed.add_field(name="AFK timeout", value=f"{int(before.afk_timeout / 60)} minutes -> {int(after.afk_timeout / 60)} minutes", inline=False)

            if before.explicit_content_filter != after.explicit_content_filter:
                before_filter = (
                    "No scan" if str(before.explicit_content_filter) == "disabled" else
                    "Scan without roles" if str(before.explicit_content_filter) == "no_role" else
                    "Scan all" if str(before.explicit_content_filter) == "all_members" else
                    "Unknown"
                )

                after_filter = (
                    "No scan" if str(after.explicit_content_filter) == "disabled" else
                    "Scan without roles" if str(after.explicit_content_filter) == "no_role" else
                    "Scan all" if str(after.explicit_content_filter) == "all_members" else
                    "Unknown"
                )

                embed.add_field(name="Explicit media filter", value=f"{before_filter} -> {after_filter}", inline=False)

            if before.icon != after.icon:
                embed.add_field(name="Server icon", value=f"[[before]]({before.icon.url if before.icon else 'none'}) -> [[after]]({after.icon.url if after.icon else 'none'})", inline=False)

            if before.name != after.name:
                embed.add_field(name="Name", value=f"{before.name} -> {after.name}")

            if before.owner != after.owner:
                embed.add_field(name="Transferred ownership", value=f"{before.owner.mention} -> {after.owner.mention}")

            if before.system_channel != after.system_channel:
                embed.add_field(name="System messages channel", value=f"{before.system_channel.mention} -> {after.system_channel.mention}", inline=False)

            if before.verification_level != after.verification_level:
                before_verification = (
                    "None" if str(before.verification_level) == "none" else
                    "Low" if str(before.verification_level) == "low" else
                    "Medium" if str(before.verification_level) == "medium" else
                    "(╯°□°）╯︵ ┻━┻" if str(before.verification_level) == "high" else
                    "┻━┻ ﾐヽ(ಠ益ಠ)ノ彡┻━┻" if str(before.verification_level) == "highest" else
                    "Unknown"
                )

                after_verification = (
                    "None" if str(after.verification_level) == "none" else
                    "Low" if str(after.verification_level) == "low" else
                    "Medium" if str(after.verification_level) == "medium" else
                    "(╯°□°）╯︵ ┻━┻" if str(after.verification_level) == "high" else
                    "┻━┻ ﾐヽ(ಠ益ಠ)ノ彡┻━┻" if str(after.verification_level) == "highest" else
                    "Unknown"
                )

                embed.add_field(name="Verification level", value=f"{before_verification} -> {after_verification}", inline=False)

            embed.set_thumbnail(url=after.icon.url)
            embed.timestamp = discord.utils.utcnow()
            embed.set_footer(text=f"Guild ID: {before.id}")

            await log_webhook.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_emojis_update(self, guild, before, after):
        log_webhook_url = await db.fetch_one("SELECT log_webhook FROM logging_webhooks WHERE guild = ?", after.guild.id)
        log_webhook = DiscordWebhookSender(url=log_webhook_url[0]) if not(log_webhook_url is None or (isinstance(log_webhook_url, tuple) and all(url is None for url in log_webhook_url))) else None

        if log_webhook:
            added_emojis = [x for x in after if x not in before]
            removed_emojis = [x for x in before if x not in after]

            if added_emojis:
                for emoji in added_emojis:
                    embed = discord.Embed(
                        title=None,
                        description=f":pencil: **Server's emojis updated!**",
                        color=0xfaa41b
                    )
                    embed.add_field(name="Added emoji", value=f":{emoji.name}:", inline=False)
                    embed.timestamp = discord.utils.utcnow()
                    embed.set_footer(text=f"Emoji ID: {emoji.id}")

                    await log_webhook.send(embed=embed)

            if removed_emojis:
                for emoji in removed_emojis:
                    embed = discord.Embed(
                        title=None,
                        description=f":pencil: **Server's emojis updated!**",
                        color=0xfaa41b
                    )
                    embed.add_field(name="Removed emoji", value=f":{emoji.name}:", inline=False)
                    embed.timestamp = discord.utils.utcnow()
                    embed.set_footer(text=f"Emoji ID: {emoji.id}")

                    await log_webhook.send(embed=embed)

            for before_emoji in before:
                for after_emoji in after:
                    if before_emoji.id == after_emoji.id and before_emoji.name != after_emoji.name:
                        embed = discord.Embed(
                            title=None,
                            description=f":pencil: **Server's emojis updated!**",
                            color=0xfaa41b
                        )
                        embed.add_field(name="Updated emoji", value=f":{before_emoji.name}: -> :{after_emoji.name}:", inline=False)
                        embed.timestamp = discord.utils.utcnow()
                        embed.set_footer(text=f"Emoji ID: {before_emoji.id}")

                        await log_webhook.send(embed=embed)

    # =============
    #  Message Log
    # =============

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.id != self.bot.user.id and not message.webhook_id and message.guild:
            log_channel_id = await db.fetch_one("SELECT log_channel FROM config WHERE guild = ?", message.guild.id)
            log_channel = self.bot.get_channel(log_channel_id[0]) if log_channel_id else None

            if message.channel.id == log_channel.id:
                return await message.delete()

            if "thanks dekko" in message.content.lower() or "thank you dekko" in message.content.lower() or "thx dekko" in message.content.lower():
                await message.add_reaction('<:dekko:1283540647969820672>')
                await message.add_reaction('\U0001f44d')

    # =============
    #  Command Log
    # =============

    @commands.Cog.listener()
    async def on_command(self, ctx):
        log_webhook_url = await db.fetch_one("SELECT log_webhook FROM logging_webhooks WHERE guild = ?", ctx.guild.id) if ctx.guild else None
        log_webhook = DiscordWebhookSender(url=log_webhook_url[0]) if not(log_webhook_url is None or (isinstance(log_webhook_url, tuple) and all(url is None for url in log_webhook_url))) else None

        if log_webhook:
            user = ctx.author
            command = ctx.command
            channel = ctx.channel

            embed = discord.Embed(
                title=None,
                description=f"{user.mention} **used a command**",
                color=discord.Colour.blurple()
            )
            embed.set_author(name=user.name, icon_url=user.display_avatar.url)
            embed.add_field(name="Command", value=f"`/{command.name}`", inline=False)
            embed.add_field(name="Channel", value=f"<#{channel.id}>", inline=False)
            embed.timestamp = discord.utils.utcnow()
            embed.set_footer(text=f"User ID: {user.id} | Channel ID: {channel.id}")

            await log_webhook.send(embed=embed)

    # ===========
    #  Error Log
    # ===========

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        error_webhook_url = await db.fetch_one("SELECT error_webhook FROM logging_webhooks WHERE guild = ?", ctx.guild.id) if ctx.guild else None
        error_webhook = DiscordWebhookSender(url=error_webhook_url[0]) if not(error_webhook_url is None or (isinstance(error_webhook_url, tuple) and all(url is None for url in error_webhook_url))) else None

        if hasattr(ctx.command, 'on_error'):
            return

        cog = ctx.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return

        error = getattr(error, 'original', error)

        if isinstance(error, commands.CommandNotFound):
            await ctx.send(":no_entry: **Invalid command!**")

        elif isinstance(error, commands.DisabledCommand):
            await ctx.send(f":no_entry: **Command** `{ctx.command}` **has been disabled.**")

        elif isinstance(error, commands.CheckFailure):
            await ctx.send(":no_entry: **ACCESS DENIED**")

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.author.send(f":no_entry: **Command** `{ctx.command}` **can not be used in Private Messages.**")
            except discord.HTTPException:
                pass

        else:
            common.logger.error(f"Ignoring exception in command {ctx.command}:\n{''.join(traceback.format_exception(type(error), error, error.__traceback__))}")
            if error_webhook: await error_webhook.send(f":no_entry: **CYKA BLYAT!**\n`DEKKO Command Processor` has encountered an error :( ```ansi\n{''.join(traceback.format_exception(type(error), error, error.__traceback__))}```")
            await ctx.send(f":no_entry: **CYKA BLYAT!**\n`DEKKO Command Processor` has encountered an error :( ```ansi\n{str(error)}```")

    # ==============
    #  Misc Logging
    # ==============

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.wait_until_ready()

        common.logger.info("[DECCYLoader] Loading Lavalink...")
        await self.bot.load_extension("extensions.dekkoplayer")
        common.logger.info("[DECCYLoader] Lavalink has loaded.")

        log_channel_id = await db.fetch_one("SELECT global_log_channel FROM global_config")
        log_channel = self.bot.get_channel(log_channel_id[0]) if log_channel_id else None

        if log_channel:
            embed = discord.Embed(
                title=None,
                description=":electric_plug: **DEKKO has (re)connected**",
                color=discord.Colour.greyple()
            )
            embed.timestamp = discord.utils.utcnow()
            
            await log_channel.send(embed=embed)

        common.logger.info("Logged in as {0.user}".format(self.bot))

    @commands.Cog.listener()
    async def on_shutdown(self):
        log_channel_id = await db.fetch_one("SELECT global_log_channel FROM global_config")
        log_channel = self.bot.get_channel(log_channel_id[0]) if log_channel_id else None

        if log_channel:
            embed = discord.Embed(
                title=None,
                description=f":electric_plug: **DEKKO was shut down**",
                color=discord.Colour.red()
            )
            embed.timestamp = discord.utils.utcnow()
            await log_channel.send(embed=embed)
            await db.close()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        log_webhook_url = await db.fetch_one("SELECT log_webhook FROM logging_webhooks WHERE guild = ?", member.guild.id)
        log_webhook = DiscordWebhookSender(url=log_webhook_url[0]) if not(log_webhook_url is None or (isinstance(log_webhook_url, tuple) and all(url is None for url in log_webhook_url))) else None

        if log_webhook:
            if before.channel is None and after.channel is not None:
                embed = discord.Embed(
                    title=None,
                    description=f":inbox_tray: {member.mention} **joined voice channel** {after.channel.mention}",
                    color=discord.Colour.green()
                )
                embed.set_author(name=member.name, icon_url=member.display_avatar.url)
                embed.timestamp = discord.utils.utcnow()

                await log_webhook.send(embed=embed)

            elif before.channel is not None and after.channel is None:
                embed = discord.Embed(
                    title=None,
                    description=f":outbox_tray: {member.mention} **left voice channel** {before.channel.mention}",
                    color=discord.Colour.red()
                )
                embed.set_author(name=member.name, icon_url=member.display_avatar.url)
                embed.timestamp = discord.utils.utcnow()

                await log_webhook.send(embed=embed)

            elif before.channel is not None and after.channel is not None and before.channel != after.channel:
                embedList = []

                leave_embed = discord.Embed(
                    title=None,
                    description=f":outbox_tray: {member.mention} **left voice channel** {before.channel.mention}",
                    color=discord.Colour.red()
                )
                leave_embed.set_author(name=member.name, icon_url=member.display_avatar.url)
                leave_embed.timestamp = discord.utils.utcnow()

                join_embed = discord.Embed(
                    title=None,
                    description=f":inbox_tray: {member.mention} **joined voice channel** {after.channel.mention}",
                    color=discord.Colour.green()
                )
                join_embed.set_author(name=member.name, icon_url=member.display_avatar.url)
                join_embed.timestamp = discord.utils.utcnow()

                embedList.append(leave_embed)
                embedList.append(join_embed)

                await log_webhook.send(embeds=embedList)
            else:
                return

async def setup(bot):
    await bot.add_cog(Events(bot))
