from discord.ext import tasks, commands

from datetime import date
from datetime import time
from datetime import timedelta

import lunardate

import common

from database import db

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
    """Calculating the date for Chinese New Year involves a lot of extremely complex math, so I use an external library"""

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

    # Thanksgiving is on the 4th Thursday of November
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

        for guild in self.bot.guilds:
            NEW_YEARS_CHANNEL_ID = await db.fetch("SELECT new_years_channel FROM holidata WHERE guild = ?", guild.id)
            CN_NEW_YEARS_CHANNEL_ID = await db.fetch("SELECT cn_new_years_channel FROM holidata WHERE guild = ?", guild.id)
            VDAY_CHANNEL_ID = await db.fetch("SELECT vday_channel FROM holidata WHERE guild = ?", guild.id)
            ST_PATTY_CHANNEL_ID = await db.fetch("SELECT st_patricks_channel FROM holidata WHERE guild = ?", guild.id)
            EASTER_CHANNEL_ID = await db.fetch("SELECT easter_channel FROM holidata WHERE guild = ?", guild.id)
            CDM_CHANNEL_ID = await db.fetch("SELECT cinco_de_mayo_channel FROM holidata WHERE guild = ?", guild.id)
            J4_CHANNEL_ID = await db.fetch("SELECT j4_channel FROM holidata WHERE guild = ?", guild.id)
            HALLOWEEN_CHANNEL_ID = await db.fetch("SELECT halloween_channel FROM holidata WHERE guild = ?", guild.id)
            THANKSGIVING_CHANNEL_ID = await db.fetch("SELECT thanksgiving_channel FROM holidata WHERE guild = ?", guild.id)
            CHRISTMAS_CHANNEL_ID = await db.fetch("SELECT christmas_channel FROM holidata WHERE guild = ?", guild.id)
            WISHLIST_CHANNEL_ID = await db.fetch("SELECT wishlist_channel FROM holidata WHERE guild = ?", guild.id)

            NEW_YEARS_CHANNEL = guild.get_channel(NEW_YEARS_CHANNEL_ID[0]) if not(NEW_YEARS_CHANNEL_ID is None or (isinstance(NEW_YEARS_CHANNEL_ID, tuple) and all(url is None for url in NEW_YEARS_CHANNEL_ID))) else None
            CN_NEW_YEARS_CHANNEL = guild.get_channel(CN_NEW_YEARS_CHANNEL_ID[0]) if not(CN_NEW_YEARS_CHANNEL_ID is None or (isinstance(CN_NEW_YEARS_CHANNEL_ID, tuple) and all(url is None for url in CN_NEW_YEARS_CHANNEL_ID))) else None
            VDAY_CHANNEL = guild.get_channel(VDAY_CHANNEL_ID[0]) if not(VDAY_CHANNEL_ID is None or (isinstance(VDAY_CHANNEL_ID, tuple) and all(url is None for url in VDAY_CHANNEL_ID))) else None
            ST_PATTY_CHANNEL = guild.get_channel(ST_PATTY_CHANNEL_ID[0]) if not(ST_PATTY_CHANNEL_ID is None or (isinstance(ST_PATTY_CHANNEL_ID, tuple) and all(url is None for url in ST_PATTY_CHANNEL_ID))) else None
            EASTER_CHANNEL = guild.get_channel(EASTER_CHANNEL_ID[0]) if not(EASTER_CHANNEL_ID is None or (isinstance(EASTER_CHANNEL_ID, tuple) and all(url is None for url in EASTER_CHANNEL_ID))) else None
            CDM_CHANNEL = guild.get_channel(CDM_CHANNEL_ID[0]) if not(CDM_CHANNEL_ID is None or (isinstance(CDM_CHANNEL_ID, tuple) and all(url is None for url in CDM_CHANNEL_ID))) else None
            J4_CHANNEL = guild.get_channel(J4_CHANNEL_ID[0]) if not(J4_CHANNEL_ID is None or (isinstance(J4_CHANNEL_ID, tuple) and all(url is None for url in J4_CHANNEL_ID))) else None
            HALLOWEEN_CHANNEL = guild.get_channel(HALLOWEEN_CHANNEL_ID[0]) if not(HALLOWEEN_CHANNEL_ID is None or (isinstance(HALLOWEEN_CHANNEL_ID, tuple) and all(url is None for url in HALLOWEEN_CHANNEL_ID))) else None
            THANKSGIVING_CHANNEL = guild.get_channel(THANKSGIVING_CHANNEL_ID[0]) if not(THANKSGIVING_CHANNEL_ID is None or (isinstance(THANKSGIVING_CHANNEL_ID, tuple) and all(url is None for url in THANKSGIVING_CHANNEL_ID))) else None
            CHRISTMAS_CHANNEL = guild.get_channel(CHRISTMAS_CHANNEL_ID[0]) if not(CHRISTMAS_CHANNEL_ID is None or (isinstance(CHRISTMAS_CHANNEL_ID, tuple) and all(url is None for url in CHRISTMAS_CHANNEL_ID))) else None
            WISHLIST_CHANNEL = guild.get_channel(WISHLIST_CHANNEL_ID[0]) if not(WISHLIST_CHANNEL_ID is None or (isinstance(WISHLIST_CHANNEL_ID, tuple) and all(url is None for url in WISHLIST_CHANNEL_ID))) else None

            if NEW_YEARS_CHANNEL:
                if (date(date.today().year, 12, 25) - timedelta(days=1) <= date.today() <= date(date.today().year, 12, 31) + timedelta(days=1)):
                    await NEW_YEARS_CHANNEL.set_permissions(NEW_YEARS_CHANNEL.guild.default_role, view_channel=None)
                elif (date(date.today().year, 1, 1) - timedelta(days=1) <= date.today() <= date(date.today().year, 1, 1) + timedelta(days=1)):
                    await NEW_YEARS_CHANNEL.set_permissions(NEW_YEARS_CHANNEL.guild.default_role, view_channel=None)
                else:
                    await NEW_YEARS_CHANNEL.set_permissions(NEW_YEARS_CHANNEL.guild.default_role, view_channel=False)

            if CN_NEW_YEARS_CHANNEL:
                # Due to the extreme complexities in determining the date for Chinese New Year, I've decided to just use a library for it
                if (get_cny_date(date.today().year) - timedelta(days=1) <= date.today() <= get_cny_date(date.today().year) + timedelta(days=1)):
                    await CN_NEW_YEARS_CHANNEL.set_permissions(CN_NEW_YEARS_CHANNEL.guild.default_role, view_channel=None)
                else:
                    await CN_NEW_YEARS_CHANNEL.set_permissions(CN_NEW_YEARS_CHANNEL.guild.default_role, view_channel=False)

            if VDAY_CHANNEL:
                if (date(date.today().year, 2, 1) - timedelta(days=1) <= date.today() <= date(date.today().year, 2, 14) + timedelta(days=1)):
                    await VDAY_CHANNEL.set_permissions(VDAY_CHANNEL.guild.default_role, view_channel=None)
                else:
                    await VDAY_CHANNEL.set_permissions(VDAY_CHANNEL.guild.default_role, view_channel=False)

            if ST_PATTY_CHANNEL:
                if (date(date.today().year, 3, 17) - timedelta(days=1) <= date.today() <= date(date.today().year, 3, 17) + timedelta(days=1)):
                    await ST_PATTY_CHANNEL.set_permissions(ST_PATTY_CHANNEL.guild.default_role, view_channel=None)
                else:
                    await ST_PATTY_CHANNEL.set_permissions(ST_PATTY_CHANNEL.guild.default_role, view_channel=False)

            if EASTER_CHANNEL:
                if (get_easter_date(date.today().year) - timedelta(days=3) <= date.today() <= get_easter_date(date.today().year) + timedelta(days=1)):
                    await EASTER_CHANNEL.set_permissions(EASTER_CHANNEL.guild.default_role, view_channel=None)
                else:
                    await EASTER_CHANNEL.set_permissions(EASTER_CHANNEL.guild.default_role, view_channel=False)

            if CDM_CHANNEL:
                if (date(date.today().year, 5, 5) - timedelta(days=1) <= date.today() <= date(date.today().year, 5, 5) + timedelta(days=1)):
                    await CDM_CHANNEL.set_permissions(CDM_CHANNEL.guild.default_role, view_channel=None)
                else:
                    await CDM_CHANNEL.set_permissions(CDM_CHANNEL.guild.default_role, view_channel=False)

            if J4_CHANNEL:
                if (date(date.today().year, 7, 4) - timedelta(days=1) <= date.today() <= date(date.today().year, 7, 4) + timedelta(days=1)):
                    await J4_CHANNEL.set_permissions(J4_CHANNEL.guild.default_role, view_channel=None)
                else:
                    await J4_CHANNEL.set_permissions(J4_CHANNEL.guild.default_role, view_channel=False)

            if HALLOWEEN_CHANNEL:
                if (date(date.today().year, 10, 1) - timedelta(days=1) <= date.today() <= date(date.today().year, 10, 31) + timedelta(days=1)):
                    await HALLOWEEN_CHANNEL.set_permissions(HALLOWEEN_CHANNEL.guild.default_role, view_channel=None)
                else:
                    await HALLOWEEN_CHANNEL.set_permissions(HALLOWEEN_CHANNEL.guild.default_role, view_channel=False)

            if THANKSGIVING_CHANNEL:
                if (date(date.today().year, 11, 1) - timedelta(days=1) <= date.today() <= get_thanksgiving_date(date.today().year) + timedelta(days=1)):
                    await THANKSGIVING_CHANNEL.set_permissions(THANKSGIVING_CHANNEL.guild.default_role, view_channel=None)
                else:
                    await THANKSGIVING_CHANNEL.set_permissions(THANKSGIVING_CHANNEL.guild.default_role, view_channel=False)

            if CHRISTMAS_CHANNEL and WISHLIST_CHANNEL:
                if (get_thanksgiving_date(date.today().year) - timedelta(days=1) <= date.today() <= date(date.today().year, 12, 25) + timedelta(days=1)):
                    await CHRISTMAS_CHANNEL.set_permissions(CHRISTMAS_CHANNEL.guild.default_role, view_channel=None)
                    await WISHLIST_CHANNEL.set_permissions(WISHLIST_CHANNEL.guild.default_role, view_channel=None)
                else:
                    await CHRISTMAS_CHANNEL.set_permissions(CHRISTMAS_CHANNEL.guild.default_role, view_channel=False)
                    await WISHLIST_CHANNEL.set_permissions(WISHLIST_CHANNEL.guild.default_role, view_channel=False)

async def setup(bot):
        await bot.add_cog(Holidays(bot))
