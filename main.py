from discord.ext import commands
import os, dotenv, discord, logging, glob, traceback
import src.cnst as cnst
import src.helpers as helpers
dotenv.load_dotenv()

logging.basicConfig(level=logging.INFO,
                    format="[%(levelname)s] %(name)s: %(message)s")

rootl = logging.getLogger()
COG_GLOB = "./src/cogs/*.py"

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=("-"),intents=discord.Intents.all()) # .all() will be changed, this is for testing
    async def setup_hook(self):
        for cogfile in glob.glob(COG_GLOB):
            # Attempts to load each functionality in the bot
            try:
                await self.load_extension("src.cogs."+cogfile.removesuffix(".py"))
            except Exception as e:
                rootl.error(f"Error loading cog {cogfile}:")
                helpers.log_exc(rootl,e)
    async def on_ready(self):
        rootl.info("Logged in successfully as {}!".format(self.user))
        rootl.info("Hello from on_ready coroutine, preparing everything...")
        rootl.info("syncing command tree with discord...")
        try:await self.tree.sync()
        except Exception as e:
            rootl.error("Error syncing command tree:")
            helpers.log_exc(rootl,e)
        rootl.info("tree synced successfully!")
        rootl.info("on_ready done!")

if __name__ == "__main__":
    bot = Bot()
    try:
        rootl.info("--- START ---")
        if not os.getenv("TOKEN"):
            raise Exception("no TOKEN found in environment!")
        bot.run(os.getenv("TOKEN"))
    except Exception as e:
        rootl.error("Error starting bot:")
        helpers.log_exc(rootl,e)