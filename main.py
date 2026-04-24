from discord.ext import commands
import os, dotenv, discord, logging, glob, traceback, asyncio, config, src.bot_class as bot_class
import src.cnst as cnst
import src.helpers as helpers
from config import *
dotenv.load_dotenv()
rootl = logging.getLogger()
logging.basicConfig(level=logging.INFO,
                    format="[%(levelname)s] %(name)s: %(message)s")
logging.getLogger("discord.client").setLevel(logging.WARNING)
logging.getLogger("discord.gateway").setLevel(logging.WARNING)

if __name__ == "__main__":
    bot = bot_class.Bot()
    try:
        rootl.info("--- START ---")
        if not os.getenv("TOKEN"):
            raise Exception("no TOKEN found in environment!")
        bot.run(os.getenv("TOKEN"))
    except Exception as e:
        rootl.error("Error starting bot:")
        helpers.log_exc(rootl,e)