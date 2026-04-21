from discord.ext import commands
import os, dotenv, discord, logging, glob, traceback
import src.cnst as cnst
dotenv.load_dotenv()
logging.basicConfig(level=logging.INFO)
rootlogger = logging.getLogger()

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=("-"),intents=discord.Intents.all()) # .all() will be changed, this is for testing
    async def setup_hook(self):
        for cogfile in glob.glob("./src/cogs/*.py"):
            # Attempts to load each functionality in the bot
            try:
                await self.load_extension("src.cogs."+cogfile.removesuffix(".py"))
            except Exception as e:
                rootlogger.error(f"Error loading cog {cogfile}:")
                rootlogger.error("".join(traceback.format_exception(e)))
    async def on_ready(self):
        rootlogger.info("Logged in successfully as {}!".format(self.user))
        rootlogger.info("Hello from on_ready coroutine, preparing everything...")
        rootlogger.info("syncing command tree with discord...")
        try:await self.tree.sync()
        except Exception as e:rootlogger.error(traceback.format_exception(e))
        rootlogger.info("tree synced successfully!")
        rootlogger.info("on_ready done!")
if __name__ == "__main__":
    bot = Bot()
    try:
        rootlogger.info("--- START ---")
        if not os.getenv("TOKEN"):
            raise Exception("no TOKEN found in environment!")
        bot.run(os.getenv("TOKEN"))
    except Exception as e:
        rootlogger.error("Error starting bot:")
        rootlogger.error("".join(traceback.format_exception(e)))