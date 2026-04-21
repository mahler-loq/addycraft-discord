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
            except Exception:
                rootlogger.error(f"Error loading cog {cogfile}:")
                rootlogger.error("".join(traceback.format_exception()))
    async def on_ready(self):
        rootlogger.info("Logged in successfully as {}!".format(self.user))
        rootlogger.info("Hello from on_ready coroutine, preparing everything...")
        rootlogger.info("syncing command tree with discord...")
        try:await self.tree.sync()
        except Exception:rootlogger.error(traceback.format_exc())
        rootlogger.info("tree synced successfully!")
        rootlogger.info("on_ready done!")
if __name__ == "__main__":
    bot = Bot()
    try:
        rootlogger.info("--- START ---")
        if not os.getenv("TOKEN"):
            rootlogger.error("no TOKEN found in environment! please add a .env file with the token, or set the environment variable in another way.")
            raise Exception("no TOKEN found in environment!")
        bot.run(os.getenv("TOKEN"))
    except Exception:
        rootlogger.error("Error starting bot:")
        rootlogger.error("".join(traceback.format_exception()))