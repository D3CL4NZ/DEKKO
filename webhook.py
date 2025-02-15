import discord
from discord import Webhook
from typing import Any, Sequence, List
import aiohttp

from discord.utils import MISSING

class DiscordWebhookSender:
    def __init__(self, url):
        self.url = url

    async def send(self, content: str = MISSING, *, username: str = MISSING, avatar_url: Any = MISSING, tts: bool = False, ephemeral: bool = False, file: discord.File = MISSING, files: Sequence[discord.File] = MISSING, embed: discord.Embed = MISSING, embeds: Sequence[discord.Embed] = MISSING, allowed_mentions: discord.AllowedMentions = MISSING, view: discord.ui.View = MISSING, thread: discord.Snowflake = MISSING, thread_name: str = MISSING, wait: bool = False, suppress_embeds: bool = False, silent: bool = False, applied_tags: List[discord.ForumTag] = MISSING, poll: discord.Poll = MISSING):
        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url(self.url, session=session)
            await webhook.send(content=content, username=username, avatar_url=avatar_url, tts=tts, ephemeral=ephemeral, file=file, files=files, embed=embed, embeds=embeds, allowed_mentions=allowed_mentions, view=view, thread=thread, thread_name=thread_name, wait=wait, suppress_embeds=suppress_embeds, silent=silent, applied_tags=applied_tags, poll=poll)
