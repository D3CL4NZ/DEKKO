import os
import unicodedata

import discord
from discord import app_commands
import yt_dlp as youtube_dl
from discord.ext import commands

# Needed for error handling
import sys
import traceback

import config

# Silence useless bug reports messages
youtube_dl.utils.bug_reports_message = lambda: ''

class YTDLError(Exception):
    pass

class YTDownload:
    @staticmethod
    async def download_video(search: str):
        base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../outtmpl')

        YTDL_OPTIONS = {
            'format': 'bestaudio/best',
            'extractaudio': True,
            'audioformat': 'mp3',
            'outtmpl': base_path + '/%(title)s.%(ext)s',
            'restrictfilenames': True,
            'noplaylist': True,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
            'default_search': 'auto',
            'source_address': '0.0.0.0',
            'writethumbnail': 'true',
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '0'
                },
                {
                    'key': 'FFmpegMetadata',
                    'add_metadata': True
                },
                {
                    'key': 'EmbedThumbnail',
                    'already_have_thumbnail': False
                }
            ]
        }

        ytdl = youtube_dl.YoutubeDL(YTDL_OPTIONS)

        data = ytdl.extract_info(search, True)

        if data is None:
            raise YTDLError('Couldn\'t find anything that matches `{}`'.format(search))

        if 'entries' not in data:
            process_info = data
        else:
            process_info = None
            for entry in data['entries']:
                if entry:
                    process_info = entry
                    break

            if process_info is None:
                raise YTDLError('Couldn\'t find anything that matches `{}`'.format(search))

        webpage_url = process_info['webpage_url']
        processed_info = ytdl.extract_info(webpage_url, True)

        if processed_info is None:
            raise YTDLError('Couldn\'t fetch `{}`'.format(webpage_url))

        if 'entries' not in processed_info:
            info = processed_info
        else:
            info = None
            while info is None:
                try:
                    info = processed_info['entries'].pop(0)
                except IndexError:
                    raise YTDLError('Couldn\'t retrieve any matches for `{}`'.format(webpage_url))

        try:
            ytdl.download(info['url'])
        except:
            raise YTDLError('Couldn\'t download {}'.format(webpage_url))

        song_path = os.path.join(base_path, youtube_dl.utils.sanitize_filename(info['title'], restricted=True) + '.mp3')
        normalized_listdirs = [os.path.join(base_path, unicodedata.normalize('NFKC', file)) for file in os.listdir(base_path)]
        full_download_path = normalized_listdirs[normalized_listdirs.index(song_path)]

        return full_download_path

class YTDLP(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        error_channel = self.bot.get_channel(config.ERROR_CHANNEL_ID)

        error = getattr(error, 'original', error)

        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
        await ctx.send(':no_entry:  **CYKA BLYAT!**\n`DEKKO-YTDLPCC.XD` has encountered an error :( ```ansi\n{}```'.format(str(error)))
        await error_channel.send(':no_entry:  **CYKA BLYAT!**\n`DEKKO-YTDLPCC.XD` has encountered an error :( ```ansi\n{}```'.format("".join(traceback.format_exception(type(error), error, error.__traceback__))))

    @commands.hybrid_command(name='ytdlp', with_app_command=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def _ytdlp(self, ctx: commands.Context, *, search: str):
        """Downloads a song"""

        async with ctx.typing():
            message = await ctx.send(":hourglass:  **Downloading audio... (This may take a while. I'll ping you when it completes)**")
        try:
            file = await YTDownload.download_video(search)
        except YTDLError as e:
            await message.edit(content=':no_entry:  **An error occurred while processing this request:** ```ansi\n{}```'.format(str(e)))
            await self.bot.get_channel(config.ERROR_CHANNEL_ID).send(':no_entry:  **An error occurred while processing this request:** ```ansi\n{}```'.format(str(e)))
        else:
            try:
                await message.edit(content=':white_check_mark:  **Download complete**')
                await ctx.channel.send("{} Here ya go pookie :3".format(ctx.author.mention), file=discord.File(file))
            except Exception as e:
                await message.edit(content=':no_entry:  **File too large for server :(**')
            os.remove(file)

async def setup(bot):
    await bot.add_cog(YTDLP(bot))
