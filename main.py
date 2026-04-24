from discord.ext import commands
import os, dotenv, discord, logging, glob, traceback, asyncio, config, src.bot_class as bot_class
import src.cnst as cnst
import src.helpers as helpers
from config import *
dotenv.load_dotenv()
rootl = logging.getLogger()
handler = logging.StreamHandler()
class ColorFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG: "\033[36m",
        logging.INFO: "\033[32m",
        logging.WARNING: "\033[33m",
        logging.ERROR: "\033[31m",
        logging.CRITICAL: "\033[41m",
    }
    RESET = "\033[0m"
    def format(self, record):
        color = self.COLORS.get(record.levelno, "")
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        record.name = f"\033[1;34m{record.name}{self.RESET}"
        return super().format(record)
handler.setFormatter(ColorFormatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s","%Y-%m-%d %H:%M:%S"))
rootl.handlers.clear()
rootl.addHandler(handler)
rootl.setLevel(logging.INFO)
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