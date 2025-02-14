from discord import Webhook, AsyncWebhookAdapter
import aiohttp

class DiscordWebhookSender:
    def __init__(self, url):
        self.url = url

    async def send(self, content=None, embed=None, username=None, avatar_url=None):
        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url(self.webhook_url, adapter=AsyncWebhookAdapter(session))
            await webhook.send(content=content, embed=embed, username=username, avatar_url=avatar_url)
