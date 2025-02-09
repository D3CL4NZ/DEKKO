import discord
from discord.ext import tasks, commands

from datetime import date
from datetime import time
from datetime import timedelta

import lunardate

import config
import common

def get_easter_date(year):
    """A helper function to calculate the date of Easter for a given year"""

    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1

    # Lots of boring math later...
    return date(year, month, day)

def get_cny_date(year):
    """Calculating the date for Chinese New Year is extremely complex so I use an external library"""

    # Chinese New Year is the first day of the first lunar month
    lunar_new_year = lunardate.LunarDate(year, 1, 1)
    # Convert lunar date to solar date
    solar_date = lunar_new_year.toSolarDate()
    return solar_date

def get_thanksgiving_date(year):
    # November 1st of the given year
    first_november = date(year, 11, 1)

    # First Thursday of November
    first_thursday = first_november + timedelta(days=(3 - first_november.weekday() + 7) % 7)

    # Thanksgiving is the 4th Thursday of November
    thanksgiving = first_thursday + timedelta(weeks=3)

    return thanksgiving

class Holidays(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        common.logger.info("[Holidays] Waiting for initialization to finish...")
        self._check_if_holiday.start()

    def cog_unload(self):
        self._check_if_holiday.cancel()

    @tasks.loop(time=time(hour=0, minute=0))
    async def _check_if_holiday(self):
        await self.bot.wait_until_ready()

        NEW_YEARS_CHANNEL = self.bot.get_channel(config.NEW_YEARS_CHANNEL_ID)
        CN_NEW_YEARS_CHANNEL = self.bot.get_channel(config.CN_NEW_YEARS_CHANNEL_ID)
        VDAY_CHANNEL = self.bot.get_channel(config.VDAY_CHANNEL_ID)
        ST_PATTY_CHANNEL = self.bot.get_channel(config.ST_PATTY_CHANNEL_ID)
        EASTER_CHANNEL = self.bot.get_channel(config.EASTER_CHANNEL_ID)
        CDM_CHANNEL = self.bot.get_channel(config.CDM_CHANNEL_ID)
        J4_CHANNEL = self.bot.get_channel(config.J4_CHANNEL_ID)
        HALLOWEEN_CHANNEL = self.bot.get_channel(config.HALLOWEEN_CHANNEL_ID)
        THANKSGIVING_CHANNEL = self.bot.get_channel(config.THANKSGIVING_CHANNEL_ID)
        CHRISTMAS_CHANNEL = self.bot.get_channel(config.CHRISTMAS_CHANNEL_ID)
        WISHLIST_CHANNEL = self.bot.get_channel(config.WISHLIST_CHANNEL_ID)

        if (date(date.today().year, 12, 25) - timedelta(days=1) <= date.today() <= date(date.today().year, 12, 31) + timedelta(days=1)):
            await NEW_YEARS_CHANNEL.set_permissions(NEW_YEARS_CHANNEL.guild.default_role, view_channel=None)
        elif (date(date.today().year, 1, 1) - timedelta(days=1) <= date.today() <= date(date.today().year, 1, 1) + timedelta(days=1)):
            await NEW_YEARS_CHANNEL.set_permissions(NEW_YEARS_CHANNEL.guild.default_role, view_channel=None)
        else:
            await NEW_YEARS_CHANNEL.set_permissions(NEW_YEARS_CHANNEL.guild.default_role, view_channel=False)

        # Due to the extreme complexities in determining the date for Chinese New Year, I've decided to just use a library for it
        if (get_cny_date(date.today().year) - timedelta(days=1) <= date.today() <= get_cny_date(date.today().year) + timedelta(days=1)):
            await CN_NEW_YEARS_CHANNEL.set_permissions(CN_NEW_YEARS_CHANNEL.guild.default_role, view_channel=None)
        else:
            await CN_NEW_YEARS_CHANNEL.set_permissions(CN_NEW_YEARS_CHANNEL.guild.default_role, view_channel=False)

        if (date(date.today().year, 2, 1) - timedelta(days=1) <= date.today() <= date(date.today().year, 2, 14) + timedelta(days=1)):
            await VDAY_CHANNEL.set_permissions(VDAY_CHANNEL.guild.default_role, view_channel=None)
        else:
            await VDAY_CHANNEL.set_permissions(VDAY_CHANNEL.guild.default_role, view_channel=False)

        if (date(date.today().year, 3, 17) - timedelta(days=1) <= date.today() <= date(date.today().year, 3, 17) + timedelta(days=1)):
            await ST_PATTY_CHANNEL.set_permissions(ST_PATTY_CHANNEL.guild.default_role, view_channel=None)
        else:
            await ST_PATTY_CHANNEL.set_permissions(ST_PATTY_CHANNEL.guild.default_role, view_channel=False)

        if (get_easter_date(date.today().year) - timedelta(days=3) <= date.today() <= get_easter_date(date.today().year) + timedelta(days=1)):
            await EASTER_CHANNEL.set_permissions(EASTER_CHANNEL.guild.default_role, view_channel=None)
        else:
            await EASTER_CHANNEL.set_permissions(EASTER_CHANNEL.guild.default_role, view_channel=False)

        if (date(date.today().year, 5, 5) - timedelta(days=1) <= date.today() <= date(date.today().year, 5, 5) + timedelta(days=1)):
            await CDM_CHANNEL.set_permissions(CDM_CHANNEL.guild.default_role, view_channel=None)
        else:
            await CDM_CHANNEL.set_permissions(CDM_CHANNEL.guild.default_role, view_channel=False)

        if (date(date.today().year, 7, 4) - timedelta(days=1) <= date.today() <= date(date.today().year, 7, 4) + timedelta(days=1)):
            await J4_CHANNEL.set_permissions(J4_CHANNEL.guild.default_role, view_channel=None)
        else:
            await J4_CHANNEL.set_permissions(J4_CHANNEL.guild.default_role, view_channel=False)

        if (date(date.today().year, 10, 1) - timedelta(days=1) <= date.today() <= date(date.today().year, 10, 31) + timedelta(days=1)):
            await HALLOWEEN_CHANNEL.set_permissions(HALLOWEEN_CHANNEL.guild.default_role, view_channel=None)
        else:
            await HALLOWEEN_CHANNEL.set_permissions(HALLOWEEN_CHANNEL.guild.default_role, view_channel=False)

        if (date(date.today().year, 11, 1) - timedelta(days=1) <= date.today() <= get_thanksgiving_date(date.today().year) + timedelta(days=1)):
            await THANKSGIVING_CHANNEL.set_permissions(THANKSGIVING_CHANNEL.guild.default_role, view_channel=None)
        else:
            await THANKSGIVING_CHANNEL.set_permissions(THANKSGIVING_CHANNEL.guild.default_role, view_channel=False)

        if (get_thanksgiving_date(date.today().year) - timedelta(days=1) <= date.today() <= date(date.today().year, 12, 25) + timedelta(days=1)):
            await CHRISTMAS_CHANNEL.set_permissions(CHRISTMAS_CHANNEL.guild.default_role, view_channel=None)
            await WISHLIST_CHANNEL.set_permissions(WISHLIST_CHANNEL.guild.default_role, view_channel=None)
        else:
            await CHRISTMAS_CHANNEL.set_permissions(CHRISTMAS_CHANNEL.guild.default_role, view_channel=False)
            await WISHLIST_CHANNEL.set_permissions(WISHLIST_CHANNEL.guild.default_role, view_channel=False)

async def setup(bot):
        await bot.add_cog(Holidays(bot))
