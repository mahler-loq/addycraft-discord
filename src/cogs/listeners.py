from discord.ext import commands
import os, dotenv, discord, logging
from src.cnst import *
from src.helpers import *
from config import *
import src.bot_class as bot_class
class MainCustomizedEventListener(commands.Cog):
    def __init__(self, bot:bot_class.Bot):
        self.bot = bot
        self._logger = logging.getLogger(self.__class__.__name__)
    def _log(self, msg:str):
        self._logger.info(msg)
    @commands.Cog.listener()
    async def on_ready(self):
        try:
            await self.bot.on_ready_lock.acquire() # run cog on_ready after root on_ready finishes
            self._log("Hello from {} on_ready event listener!".format(self.__class__.__name__))
            if AUTOLEAVE_UNTRUSTED_SERVERS or STRICT_SECURITY:
                for guild in self.bot.guilds:
                    if guild.id not in (main_server_id, staff_server_id):
                        self._logger.warning("Bot is in an untrusted server on startup, leaving it automatically due to AUTOLEAVE_UNTRUSTED_SERVERS or STRICT_SECURITY being set.")
                        self._logger.warning("\tServer name: {}".format(guild.name))
                        self._logger.warning("\tServer ID: {}".format(guild.id))
                        try:await guild.leave()
                        except Exception as e:
                            self._logger.warning("Failed to leave untrusted server: {}".format(e))
                            log_exc(self._logger, e)
            else:
                self._log("Nothing to do.")
        finally:
            self._log("on_ready finished, releasing lock...")
            self.bot.on_ready_lock.release() # release lock so cog on_ready functions can run if they need to
    @commands.Cog.listener()
    async def on_guild_join(self,guild:discord.Guild):
        if AUTOLEAVE_UNTRUSTED_SERVERS or STRICT_SECURITY:
            self._logger.warning("Bot has joined an untrusted server, leaving it automatically due to AUTOLEAVE_UNTRUSTED_SERVERS or STRICT_SECURITY being set.")
            self._logger.warning("\tServer name: {}".format(guild.name))
            self._logger.warning("\tServer ID: {}".format(guild.id))
            try:await guild.leave()
            except Exception as e:
                self._logger.warning("Failed to leave untrusted server: {}".format(e))
                log_exc(self._logger, e)
        else:
            self._log("Bot joined server:")
            self._log("\tServer name: {}".format(guild.name))
            self._log("\tServer ID: {}".format(guild.id))
    @commands.Cog.listener()
    async def on_memeber_join(self, member:discord.Member):
        joined_server="main server" if member.guild.id==main_server_id else "staff server" if member.guild.id==staff_server_id else "unknown server"
        self._log("Member joined {}: {} ({})".format(joined_server, member.display_name, member.id))
        if member.guild.id==staff_server_id:
            await self.bot.get_channel(staff_entry_channel_id).send("Welcome, {}, to the AddyCraft Staff Discord Server. If you were invited by a member of management, please wait here while we get things sorted. Onboarding can take anywhere from a few minutes, up to a maximum of a few hours. Please be patient while we go through all of our onboard members in the order they joined. If you have yet to receive access to the rest of the server within 6 hours, please message an Owner or a Sr Admin to be manually verified. Thanks for your interest in joining staff, and we look forward to knowing you better.".format(member.mention))
        elif member.guild.id==main_server_id:
            await self.bot.get_channel(mainserver_entry_channel_id).send("Welcome, {} has joined the server! Please make sure to read the rules and look at any posted announcements for any important information posted recently. If you need any help, check out our Community Support channel or our Tickets channel. Thanks for joining and we are really glad to have you!".format(member.mention))
        else:
            if not (STRICT_SECURITY or AUTOLEAVE_UNTRUSTED_SERVERS):
                self._logger.warning("Someone just joined an unknown server, this likely means the bot has been invited somewhere it shouldn't have been invited.")
                self._logger.warning("Member: {} ({}), Server: {} ({}), can we create an invite there? {}".format(member.display_name, member.id, member.guild.name, member.guild.id, "Yes, you may want to join it to check out what the unrecognised server is"if member.guild.get_member(self.bot.user.id).guild_permissions.create_instant_invite else "No, but the server can be automatically left if the bot is started with the STRICT_SECURITY flag set in the configuration file."))
            else:
                self._logger.warning("Someone just joined an unknown server, leaving it automatically due to AUTOLEAVE_UNTRUSTED_SERVERS or STRICT_SECURITY being set.")
                try:
                    await member.guild.leave()
                except Exception as e:
                    self._logger.warning("Failed to leave unknown server: {}".format(e))
                    log_exc(self._logger, e)
async def setup(bot):
    cog = MainCustomizedEventListener(bot)
    await bot.add_cog(cog)
    cog._log("loaded successfully!")

##DEVNOTES:
## .format() and ondef type annotations are NOT used in an attempt to be
## in the very least compatible with older versions of python.
## This isn't required, and i will likely stop doing this in the future,
## but it's nice to have in case this project needs to be run on a machine supporting only older python versions.