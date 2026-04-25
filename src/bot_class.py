from discord.ext import commands
import os, dotenv, discord, logging, glob, traceback, asyncio, config
import src.cnst as cnst
import src.helpers as helpers
from fixedstr import *
from config import *
rootl = logging.getLogger()
class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="NOPREFIX",intents=discord.Intents.all(),help_command=None) # .all() will be changed, this is for testing
        self.on_ready_lock = asyncio.Lock() # allows only one on_ready to run at a time
    async def setup_hook(self):
        await self.on_ready_lock.acquire() # so cogs don't run their on_ready code before the root on_ready has finished
        for cogfile in glob.glob(COG_GLOB):
            # Attempts to load each functionality in the bot (src/cogs/*.py), log to console on fail
            if cogfile.endswith("__init__.py") or not cogfile:continue # skip __init__.py files and empty results
            try:
                await self.load_extension("src.cogs."+os.path.basename(cogfile).removesuffix(".py"))
            except Exception as e:
                rootl.error(f"Error loading cog {cogfile}:")
                helpers.log_exc(rootl,e)
    async def on_ready(self):
        # on_ready is called when the bot has finished preparing the data received from discord after login
        rootl.info("Logged in successfully as {}!".format(self.user))
        rootl.info("Hello from root on_ready coroutine! preparing everything...")
        rootl.info("Dumping configuration options from config.py...")
        for var in dir(config):
            if var.isupper():
                rootl.info("\t{}: {}".format(var, getattr(config, var)))
        rootl.info("syncing command tree with discord...")
        try:await self.tree.sync()  # this is required for slash commands to work, it syncs the commands defined in the code with discord's servers
        except Exception as e:
            rootl.error("Error syncing command tree:")
            helpers.log_exc(rootl,e)
        rootl.info("tree synced successfully!")
        rootl.info("on_ready done!")
        self.on_ready_lock.release() # allow cog on_ready functions to run if they need to
