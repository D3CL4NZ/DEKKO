import re

import discord
import lavalink
from discord import app_commands
from discord.ext import commands
from lavalink.events import TrackStartEvent, QueueEndEvent
from lavalink.errors import ClientError
from lavalink.filters import LowPass
from lavalink.server import LoadType

import config
import common

url_rx = re.compile(r'https?://(?:www\.)?.+')

class LavalinkVoiceClient(discord.VoiceProtocol):
    """
    This is the preferred way to handle external voice sending
    This client will be created via a cls in the connect method of the channel
    see the following documentation:
    https://discordpy.readthedocs.io/en/latest/api.html#voiceprotocol
    """

    def __init__(self, client: discord.Client, channel: discord.abc.Connectable):
        self.client = client
        self.channel = channel
        self.guild_id = channel.guild.id
        self._destroyed = False

        if not hasattr(self.client, 'lavalink'):
            # Instantiate a client if one doesn't exist.
            # We store it in `self.client` so that it may persist across cog reloads,
            # however this is not mandatory.
            self.client.lavalink = lavalink.Client(client.user.id)
            self.client.lavalink.add_node(host=config.LL_HOST, port=config.LL_PORT, password=config.LL_PASSWORD,
                                          region='us', name='default-node')

        # Create a shortcut to the Lavalink client here.
        self.lavalink = self.client.lavalink

    async def on_voice_server_update(self, data):
        # the data needs to be transformed before being handed down to
        # voice_update_handler
        lavalink_data = {
            't': 'VOICE_SERVER_UPDATE',
            'd': data
        }
        await self.lavalink.voice_update_handler(lavalink_data)

    async def on_voice_state_update(self, data):
        channel_id = data['channel_id']

        if not channel_id:
            await self._destroy()
            return

        self.channel = self.client.get_channel(int(channel_id))

        # the data needs to be transformed before being handed down to
        # voice_update_handler
        lavalink_data = {
            't': 'VOICE_STATE_UPDATE',
            'd': data
        }

        await self.lavalink.voice_update_handler(lavalink_data)

    async def connect(self, *, timeout: float, reconnect: bool, self_deaf: bool = False, self_mute: bool = False) -> None:
        """
        Connect the bot to the voice channel and create a player_manager
        if it doesn't exist yet.
        """
        # ensure there is a player_manager when creating a new voice_client
        self.lavalink.player_manager.create(guild_id=self.channel.guild.id)
        await self.channel.guild.change_voice_state(channel=self.channel, self_mute=self_mute, self_deaf=self_deaf)

    async def disconnect(self, *, force: bool = False) -> None:
        """
        Handles the disconnect.
        Cleans up running player and leaves the voice client.
        """
        player = self.lavalink.player_manager.get(self.channel.guild.id)

        # no need to disconnect if we are not connected
        if not force and not player.is_connected:
            return

        # None means disconnect
        await self.channel.guild.change_voice_state(channel=None)

        # update the channel_id of the player to None
        # this must be done because the on_voice_state_update that would set channel_id
        # to None doesn't get dispatched after the disconnect
        player.channel_id = None
        await self._destroy()

    async def _destroy(self):
        self.cleanup()

        if self._destroyed:
            # Idempotency handling, if `disconnect()` is called, the changed voice state
            # could cause this to run a second time.
            return

        self._destroyed = True

        try:
            await self.lavalink.player_manager.destroy(self.guild_id)
        except ClientError:
            pass


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        if not hasattr(bot, 'lavalink'):
            bot.lavalink = lavalink.Client(bot.user.id)
            bot.lavalink.add_node(host=config.LL_HOST, port=config.LL_PORT, password=config.LL_PASSWORD,
                                  region='us', name='default-node')

        self.lavalink: lavalink.Client = bot.lavalink
        self.lavalink.add_event_hooks(self)

    def cog_unload(self):
        """
        This will remove any registered event hooks when the cog is unloaded.
        They will subsequently be registered again once the cog is loaded.

        This effectively allows for event handlers to be updated when the cog is reloaded.
        """
        self.lavalink._event_hooks.clear()

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send(f":no_entry:  **{error.original}**")

    async def create_player(ctx: commands.Context):
        """
        A check that is invoked before any commands marked with `@commands.check(create_player)` can run.

        This function will try to create a player for the guild associated with this Context, or raise
        an error which will be relayed to the user if one cannot be created.
        """
        if ctx.guild is None:
            raise commands.NoPrivateMessage()

        player = ctx.bot.lavalink.player_manager.create(ctx.guild.id)
        # Create returns a player if one exists, otherwise creates.
        # This line is important because it ensures that a player always exists for a guild.

        # Most people might consider this a waste of resources for guilds that aren't playing, but this is
        # the easiest and simplest way of ensuring players are created.

        # These are commands that require the bot to join a voicechannel (i.e. initiating playback).
        # Commands such as volume/skip etc don't require the bot to be in a voicechannel so don't need listing here.
        should_connect = ctx.command.name in ('play',)

        voice_client = ctx.voice_client

        if not ctx.author.voice or not ctx.author.voice.channel:
            # Check if we're in a voice channel. If we are, tell the user to join our voice channel.
            if voice_client is not None:
                raise commands.CommandInvokeError('You need to join my voice channel first')

            # Otherwise, tell them to join any voice channel to begin playing music.
            raise commands.CommandInvokeError('You need to join a voice channel first')

        voice_channel = ctx.author.voice.channel

        if voice_client is None:
            if not should_connect:
                raise commands.CommandInvokeError("I'm not playing anything")

            permissions = voice_channel.permissions_for(ctx.me)

            if not permissions.connect or not permissions.speak:
                raise commands.CommandInvokeError('I need the `CONNECT` and `SPEAK` permissions')

            if voice_channel.user_limit > 0:
                # A limit of 0 means no limit. Anything higher means that there is a member limit which we need to check.
                # If it's full, and we don't have "move members" permissions, then we cannot join it.
                if len(voice_channel.members) >= voice_channel.user_limit and not ctx.me.guild_permissions.move_members:
                    raise commands.CommandInvokeError('Your voice channel is full!')

            player.store('channel', ctx.channel.id)
            await ctx.author.voice.channel.connect(cls=LavalinkVoiceClient, self_deaf=True)
        elif voice_client.channel.id != voice_channel.id:
            raise commands.CommandInvokeError('You need to join my voice channel first')

        return True
    
    @staticmethod
    def parse_duration(duration: int):
        duration = duration // 1000  # Convert milliseconds to seconds
        minutes, seconds = divmod(duration, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)

        duration_parts = []
        if days > 0:
            duration_parts.append(f'{days}:{hours:02}:{minutes:02}:{seconds:02}')
        elif hours > 0:
            duration_parts.append(f'{hours}:{minutes:02}:{seconds:02}')
        else:
            duration_parts.append(f'{minutes}:{seconds:02}')

        return ''.join(duration_parts)

    @lavalink.listener(TrackStartEvent)
    async def on_track_start(self, event: TrackStartEvent):
        guild_id = event.player.guild_id
        channel_id = event.player.fetch('channel')
        guild = self.bot.get_guild(guild_id)

        if not guild:
            return await self.lavalink.player_manager.destroy(guild_id)

        channel = guild.get_channel(channel_id)

        if channel:
            await channel.send(embed=discord.Embed(
                title=':musical_note:  Now Playing',
                description=f'```\n{event.track.title}\n```',
                color=0xda00ff)
            .add_field(name='Duration', value=self.parse_duration(event.track.duration))
            .add_field(name='Requested by', value=f"<@{event.track.requester}>")
            .add_field(name='Uploader', value=event.track.author)
            .add_field(name='URL', value=f'[Click]({event.track.uri})')
            .set_thumbnail(url=event.track.artwork_url)
            .set_footer(text=f"DEKKOPlayer Redux v1.0.2 | DEKKO! v{common.VERSION}", icon_url="attachment://dekko_record.gif"), file=discord.File("./img/dekko_record.gif", "dekko_record.gif"))

    @lavalink.listener(QueueEndEvent)
    async def on_queue_end(self, event: QueueEndEvent):
        guild_id = event.player.guild_id
        guild = self.bot.get_guild(guild_id)

        if guild is not None:
            await guild.voice_client.disconnect(force=True)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # Check if the bot is in a voice channel
        if not member.guild.voice_client:
            return

        # Check if the bot is alone in the voice channel
        voice_channel = member.guild.voice_client.channel
        if len(voice_channel.members) == 1 and voice_channel.members[0] == member.guild.me:
            player = self.bot.lavalink.player_manager.get(member.guild.id)
            channel_id = player.fetch('channel')
            text_channel = self.bot.get_channel(channel_id)
            await member.guild.voice_client.disconnect()
            if text_channel:
                await text_channel.send(":microphone:  **DEKKO out** *\*mic drop\**")

    @commands.hybrid_group(invoke_without_command=True)
    @app_commands.allowed_installs(guilds=True, users=False)
    @app_commands.allowed_contexts(guilds=True, dms=False, private_channels=True)
    async def dp(self, ctx):
        await ctx.send(':warning:  **You must specify a subcommand**')

    @dp.command(name='play', with_app_command=True)
    @app_commands.allowed_installs(guilds=True, users=False)
    @app_commands.allowed_contexts(guilds=True, dms=False, private_channels=True)
    @commands.check(create_player)
    async def _play(self, ctx, *, query: str):
        """Searches and plays a song from a given query"""
        # Get the player for this guild from cache.
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        # Remove leading and trailing <>. <> may be used to suppress embedding links in Discord.
        query = query.strip('<>')

        # Check if the user input might be a URL. If it isn't, we can Lavalink do a YouTube search for it instead.
        # SoundCloud searching is possible by prefixing "scsearch:" instead.
        if not url_rx.match(query):
            query = f'ytsearch:{query}'

        # Get the results for the query from Lavalink.
        results = await player.node.get_tracks(query)

        embed = discord.Embed(color=0xda00ff)

        # Valid load_types are:
        #   TRACK    - direct URL to a track
        #   PLAYLIST - direct URL to playlist
        #   SEARCH   - query prefixed with either "ytsearch:" or "scsearch:". This could possibly be expanded with plugins.
        #   EMPTY    - no results for the query (result.tracks will be empty)
        #   ERROR    - the track encountered an exception during loading
        if results.load_type == LoadType.EMPTY:
            return await ctx.send("I couldn't find any tracks for that query.")
        elif results.load_type == LoadType.PLAYLIST:
            tracks = results.tracks

            # Add all of the tracks from the playlist to the queue.
            for track in tracks:
                # requester isn't necessary but it helps keep track of who queued what.
                # You can store additional metadata by passing it as a kwarg (i.e. key=value)
                player.add(track=track, requester=ctx.author.id)

            embed.title = ':arrow_heading_down:  Playlist Enqueued!'
            embed.description = f'{results.playlist_info.name} - {len(tracks)} tracks'
        else:
            track = results.tracks[0]
            embed.title = ':arrow_heading_down:  Track Enqueued'
            embed.description = f'[{track.title}]({track.uri})'

            # requester isn't necessary but it helps keep track of who queued what.
            # You can store additional metadata by passing it as a kwarg (i.e. key=value)
            player.add(track=track, requester=ctx.author.id)

        await ctx.send(embed=embed)

        # We don't want to call .play() if the player is playing as that will effectively skip
        # the current track.
        if not player.is_playing:
            await player.play()

    @dp.command(name='pause', with_app_command=True)
    @app_commands.allowed_installs(guilds=True, users=False)
    @app_commands.allowed_contexts(guilds=True, dms=False, private_channels=True)
    @commands.check(create_player)
    async def _pause(self, ctx):
        """Pauses the currently playing track"""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send("No track is currently playing.")

        await player.set_pause(True)
        await ctx.send(":pause_button:  **Paused the track**")

    @dp.command(name='resume', with_app_command=True)
    @app_commands.allowed_installs(guilds=True, users=False)
    @app_commands.allowed_contexts(guilds=True, dms=False, private_channels=True)
    @commands.check(create_player)
    async def _resume(self, ctx):
        """Resumes the currently paused track"""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send("No track is currently playing.")

        await player.set_pause(False)
        await ctx.send(":play_pause:  **Resumed the track**")

    @dp.command(name='volume', with_app_command=True)
    @app_commands.allowed_installs(guilds=True, users=False)
    @app_commands.allowed_contexts(guilds=True, dms=False, private_channels=True)
    @commands.check(create_player)
    async def _volume(self, ctx, volume: int):
        """Sets the volume of the player"""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        # Ensure volume is within the acceptable range
        volume = max(0, min(100, volume))

        await player.set_volume(volume)
        await ctx.send(f":speaker:  **Volume set to {volume}%**")

    @dp.command(name='stop', with_app_command=True)
    @app_commands.allowed_installs(guilds=True, users=False)
    @app_commands.allowed_contexts(guilds=True, dms=False, private_channels=True)
    @commands.check(create_player)
    async def _stop(self, ctx):
        """Stops the currently playing track and clears the queue"""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send("No track is currently playing.")

        # Stop the current track
        await player.stop()
        # Clear the queue
        player.queue.clear()
        await ctx.send(":stop_button:  **Stopped playback and cleared the queue**")

    @dp.command(name='skip', with_app_command=True)
    @app_commands.allowed_installs(guilds=True, users=False)
    @app_commands.allowed_contexts(guilds=True, dms=False, private_channels=True)
    @commands.check(create_player)
    async def _skip(self, ctx):
        """Skips the currently playing track"""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send("No track is currently playing.")

        await player.skip()
        await ctx.send(":track_next:  **Skipped the current track**")

    @dp.command(name='loop', with_app_command=True)
    @app_commands.allowed_installs(guilds=True, users=False)
    @app_commands.allowed_contexts(guilds=True, dms=False, private_channels=True)
    @commands.check(create_player)
    async def _loop(self, ctx):
        """Toggles looping of the currently playing track"""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send("No track is currently playing.")

        player.set_loop(not player.loop)
        loop_status = "enabled" if player.loop else "disabled"
        await ctx.send(f":repeat:  **Looping {loop_status}**")

    @dp.command(name='queue', with_app_command=True)
    @app_commands.allowed_installs(guilds=True, users=False)
    @app_commands.allowed_contexts(guilds=True, dms=False, private_channels=True)
    @commands.check(create_player)
    async def _queue(self, ctx):
        """Displays the current queue"""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.queue:
            return await ctx.send("The queue is currently empty.")

        embed = discord.Embed(title=":books:  Current Queue", color=0xda00ff)
        for index, track in enumerate(player.queue, start=1):
            embed.add_field(name=f"{index}. {track.title}", value=f"Requested by <@{track.requester}>", inline=False)

        await ctx.send(embed=embed)

    @dp.command(name='remove', with_app_command=True)
    @app_commands.allowed_installs(guilds=True, users=False)
    @app_commands.allowed_contexts(guilds=True, dms=False, private_channels=True)
    @commands.check(create_player)
    async def _remove(self, ctx, index: int):
        """Removes a song from the queue at the given index"""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.queue:
            return await ctx.send("The queue is currently empty.")

        if index < 1 or index > len(player.queue):
            return await ctx.send("Invalid index. Please provide a valid index.")

        removed_track = player.queue.pop(index - 1)
        await ctx.send(f":eject:  **Popped** `{removed_track.title}` **from the queue**")

    @dp.command(name='lowpass', with_app_command=True)
    @app_commands.allowed_installs(guilds=True, users=False)
    @app_commands.allowed_contexts(guilds=True, dms=False, private_channels=True)
    @commands.check(create_player)
    async def _lowpass(self, ctx, strength: float):
        """Sets the strength of the low pass filter"""
        # Get the player for this guild from cache.
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        # This enforces that strength should be a minimum of 0.
        # There's no upper limit on this filter.
        strength = max(0.0, strength)

        # Even though there's no upper limit, we will enforce one anyway to prevent
        # extreme values from being entered. This will enforce a maximum of 100.
        strength = min(100, strength)

        embed = discord.Embed(color=0xda00ff, title=':chart_with_downwards_trend:  Low Pass Filter')

        # A strength of 0 effectively means this filter won't function, so we can disable it.
        if strength == 0.0:
            await player.remove_filter('lowpass')
            embed.description = 'Disabled **Low Pass Filter**'
            return await ctx.send(embed=embed)

        # Lets create our filter.
        low_pass = LowPass()
        low_pass.update(smoothing=strength)  # Set the filter strength to the user's desired level.

        # This applies our filter. If the filter is already enabled on the player, then this will
        # just overwrite the filter with the new values.
        await player.set_filter(low_pass)

        embed.description = f'Set **Low Pass Filter** strength to {strength}.'
        await ctx.send(embed=embed)

    @dp.command(name='leave', aliases=['disconnect'], with_app_command=True)
    @app_commands.allowed_installs(guilds=True, users=False)
    @app_commands.allowed_contexts(guilds=True, dms=False, private_channels=True)
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_guild=True))
    @commands.check(create_player)
    async def _leave(self, ctx):
        """Disconnects the player from the voice channel and clears its queue"""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        # The necessary voice channel checks are handled in "create_player."
        # We don't need to duplicate code checking them again.

        # Clear the queue to ensure old tracks don't start playing
        # when someone else queues something.
        player.queue.clear()
        # Stop the current track so Lavalink consumes less resources.
        await player.stop()
        # Disconnect from the voice channel.
        await ctx.voice_client.disconnect(force=True)
        await ctx.send(":microphone:  **DEKKO out** *\*mic drop\**")


async def setup(bot):
    await bot.add_cog(Music(bot))