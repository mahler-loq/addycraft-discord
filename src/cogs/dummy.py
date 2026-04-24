from discord.ext import commands
import os, dotenv, discord, logging
from src import bot_class

class DummyCog(commands.Cog):
    def __init__(self, bot:bot_class.Bot):
        self.bot = bot
        self._logger = logging.Logger(self.__class__.__name__, logging.INFO)
    def _log(self, msg:str):
        self._logger.info(msg)

async def setup(bot):
    cog = DummyCog(bot)
    await bot.add_cog(cog)
    cog._log("loaded successfully!")

# This file is meant to be a template for new cogs. It doesn't do anything by design, only makes my life easier so i don't
# have to rewrite the same code every time i create a functionality cog.

##DEVNOTES:
## .format() and ondef type annotations are NOT used in an attempt to be
## in the very least compatible with older versions of python.
## This isn't required, and i will likely stop doing this in the future,
## but it's nice to have in case this project needs to be run on a machine supporting only older python versions.