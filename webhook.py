from discord import Webhook
import aiohttp

class DiscordWebhookSender:
    def __init__(self, url):
        self.url = url

    async def send(self, content=None, *, username=None, avatar_url=None, embed=None, embeds=None):
        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url(self.url, session=session)
            if embeds and not embed:
                await webhook.send(content=content, username=username, avatar_url=avatar_url, embeds=embeds)
            else:
                await webhook.send(content=content, username=username, avatar_url=avatar_url, embed=embed)
