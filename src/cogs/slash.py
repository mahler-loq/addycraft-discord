import traceback,io
from discord.ext import commands
from discord import app_commands
import os, dotenv, discord, logging, discord.ui as ui
from fixedstr import *
from src.helpers import PermissionTier as pt, log_exc, codeblock_wrap, fresh
from src.cnst import *
import src.bot_class as bot_class
class RankRequestContainer(ui.Container):
    def __init__(self, author:discord.Member, rank:int, message:str):
        super().__init__()
        self.author = author
        self.rank = rank
        self.message = message
        self.add_item(ui.TextDisplay(content="## New Rank Request"))
        self.add_item(ui.Separator())
        self.add_item(ui.TextDisplay(content="{} is requesting a <@&{}> for help.".format(self.author.mention, self.rank)))
        self.add_item(ui.TextDisplay(content="Reason for the request: **{}**".format(self.message)))
        self.add_item(ui.Separator())
        self.add_item(ui.TextDisplay(content="Requested at: <t:{}:f>".format(int(discord.utils.utcnow().timestamp()))))
class WhoAmIContainer(ui.Container):
    def __init__(self, user:discord.Member, advanced:bool=False):
        super().__init__()
        self.ptt = pt(user)
        self.user = user
        self.advanced = advanced
    async def setup(self):
        self.add_item(ui.TextDisplay(content="## Information for {}".format(self.user.mention)))
        self.add_item(ui.Separator())
        self.add_item(ui.TextDisplay(content="Your display name: **{}**".format(self.user.display_name)))
        self.add_item(ui.TextDisplay(content="Your Discord ID: **{}**".format(self.user.id)))
        self.add_item(ui.TextDisplay(content="Your In-game name: **{}**".format(PCD)))
        self.add_item(ui.TextDisplay(content="Staff Member: **{}**".format("Yes" if self.ptt.staff else "No")))
        if self.advanced:
            self.add_item(ui.Separator())
            self.add_item(ui.TextDisplay(content="Your permission tier: **{} [{}]**".format(self.ptt.name, self.ptt.value)))
            self.add_item(ui.TextDisplay(content="Internal Developer: **{}**".format("Yes" if self.ptt.DEV else "No")))
            self.add_item(ui.TextDisplay(content="Special Tiers: **{}**".format(self.ptt.special_pretty)))
            if await self.bot.get_cog("DatabaseModule").kv_bl_exists(self.user.id):
                self.add_item(ui.Separator())
                self.add_item(ui.TextDisplay(content="**Special Data**"))
                self.add_item(ui.File("attachment://{}.bin".format(await self.bot.get_cog("DatabaseModule").kv_bl_hash(self.user.id))))
class BoloContainer(ui.Container):
    def __init__(self, ign:str, user_id:int, username:str, author:int, reason:str):
        super().__init__()
        self.add_item(ui.TextDisplay(content="## New BOLO Published"))
        self.add_item(ui.Separator())
        self.add_item(ui.TextDisplay(content="A new bolo has been published by {}".format(author)))
        self.add_item(ui.Separator())
        self.add_item(ui.TextDisplay(content="In Game Name of the Offender: `{}`".format(ign)))
        self.add_item(ui.TextDisplay(content="Discord Username of the Offender: `{}`".format(username)))
        self.add_item(ui.TextDisplay(content="Discord User ID of the Offender: `{}`".format(user_id)))
        self.add_item(ui.Separator())
        self.add_item("Reason: {}".format(reason if reason else "No reason provided."))
class SeparatedTextContainer(ui.Container):
    def __init__(self, title:str, text:str, ping:discord.Role|discord.User=None, author:str=None):
        super().__init__()
        self.title = title
        self.text = text
        self.ping = ping.mention
        if ping is not None:
            self.add_item(ui.TextDisplay(content=self.ping))
            self.add_item(ui.Separator())
        self.add_item(ui.TextDisplay(content="## "+self.title))
        self.add_item(ui.TextDisplay(content=self.text))
        if author is not None:
            self.add_item(ui.Separator())
            self.add_item(ui.TextDisplay(content="`Sent by {}`".format(author)))
class UserHiredContainer(ui.Container):
    def __init__(self, user:discord.Member, author:discord.Member, url:str):
        super().__init__()
        self.user = user
        self.author = author
        self.url = url
        self.add_item(ui.TextDisplay(content="## Application approved!"))
        self.add_item(ui.Separator())
        self.add_item(ui.TextDisplay(content="""Congratulations, {}\n\nYour application has been approved by {}. Thank you so much for your consideration in joining the staff team and we really look forward to working with you. Below will be a link to our Staff Discord Server.""".format(self.user.mention, self.author.mention)))
        self.add_item(ui.Separator())
        self.add_item(ui.Button(label="Join the Staff Server", url=url, style=discord.ButtonStyle.success))
class UserFiredContainer(ui.Container):
    def __init__(self, user:discord.Member, author:discord.Member, reason:str=None):
        super().__init__()
        self.user = user
        self.author = author
        self.add_item(ui.TextDisplay(content="## Staff Position Terminated"))
        self.add_item(ui.Separator())
        self.add_item(ui.TextDisplay("""We regret to inform you that your position on the staff team has been terminated by {}.\n\nReason:\n{}\n\nIf you have any questions regarding this decision, please feel free to reach out to any of the current staff members for more information.""".format(self.author.mention, reason if reason is not None else "No reason provided.")))
class UserPromotedContainer(ui.Container):
    def __init__(self, user:discord.Member, author:discord.Member, new:int, reason:str):
        super().__init__()
        self.user = user
        self.author = author
        self.new = new
        self.reason = reason
        self.add_item(ui.TextDisplay(content="## Staff Position Promoted"))
        self.add_item(ui.Separator())
        self.add_item(ui.TextDisplay(content="Congratulations, {}!\n\nYou have been promoted to `{}` by {}.\n\nReason:\n{}".format(self.user.mention, pt.ttn(self.new), self.author.mention, self.reason if self.reason is not None else "No reason provided.")))
class UserDemotedContainer(ui.Container):
    def __init__(self, user:discord.Member, author:discord.Member, new:int, reason:str):
        super().__init__()
        self.user = user
        self.author = author
        self.new = new
        self.reason = reason
        self.add_item(ui.TextDisplay(content="## Staff Position Demoted"))
        self.add_item(ui.Separator())
        self.add_item(ui.TextDisplay(content="We regret to inform you that you have been demoted to `{}` by {}.\n\nReason:\n{}".format(pt.ttn(self.new), self.author.mention, self.reason if self.reason is not None else "No reason provided.")))
class BasicSlashCommands(commands.Cog):
    staff=app_commands.Group(name="staff",description="Commands to manage the staff team")
    steam=app_commands.Group(name="team",description="Commands for the staff server",guild_ids=[staff_server_id])
    def __init__(self, bot:bot_class.Bot):
        self.bot = bot
        self._logger = logging.getLogger(self.__class__.__name__)
    def _log(self, msg:str):
        self._logger.info(msg)
    @app_commands.command(name="announce", description="Sends an announcement to the specified channel, optionally pinging a role.")
    async def announce(self, interaction: discord.Interaction, channel: discord.TextChannel, title: str, text: str, ping: discord.Role = None):
        ptu = pt(interaction.user)
        #~ begin block early return
        if not ptu.administrative:
            return await interaction.response.send_message(noperm, ephemeral=True)
        #~ finish block early return
        try:
            cont = SeparatedTextContainer(title, text, ping, interaction.user.display_name)
            await channel.send(view=ui.LayoutView(timeout=0).add_item(cont))
            await interaction.response.send_message("Announcement sent successfully!", ephemeral=True)
        except Exception as e:
            log_exc(self._logger, e)
            await interaction.response.send_message("An error occurred while sending the announcement.\n"+codeblock_wrap(traceback.format_exception(e)), ephemeral=True)
    @staff.command(name="hire", description="Hires a user as a helper.")
    async def hire(self, interaction: discord.Interaction, user: discord.Member):
        ptu = pt(interaction.user)
        ptt = pt(user)
        #~ begin block early return
        if not ptu.sr_administrative:
            return await interaction.response.send_message(noperm, ephemeral=True)
        if ptt.staff:
            return await interaction.response.send_message("User is already apart of staff, perhaps you meant to `/promote` them?", ephemeral=True)
        #~ finish block early return
        try:
            self._log("{} hired {}".format(interaction.user.display_name, user.display_name))
            url=(await(self.bot.get_channel(staff_entry_channel_id)).create_invite(max_uses=1, max_age=0)).url
            await user.send(view=ui.LayoutView(timeout=0).add_item(UserHiredContainer(user, interaction.user, url)))
            await user.add_roles(interaction.guild.get_role(helper_role_ids[0]), reason="Hired as helper by {}".format(interaction.user.display_name))
        except Exception as e:
            log_exc(self._logger, e)
            return await interaction.response.send_message("An error occurred while hiring the user.\n"+codeblock_wrap(traceback.format_exception(e)), ephemeral=True)
        await interaction.response.send_message("`{}` hired successfully! Make sure to remember to manually give them their `Helper` rank when they join the staff server.".format(user.display_name), ephemeral=True)
    @staff.command(name="fire", description="Fires a user from their staff position.")
    async def fire(self, interaction: discord.Interaction, user: discord.Member, reason: str = None):
        ptu = pt(interaction.user)
        ptt = pt(user)
        #~ begin block early return
        if not ptu.sr_administrative:
            return await interaction.response.send_message(noperm, ephemeral=True)
        if ptt.sr_administrative:
            return await interaction.response.send_message("You cannot fire this user, they are at a higher or equal staff rank than you.", ephemeral=True)
        if ptt.nstaff:
            return await interaction.response.send_message("You cannot fire this user as they are currently not a staff member.", ephemeral=True)
        #~ finish block early return
        try:
            self._log("{} fired {}".format(interaction.user.display_name, user.display_name))
            await user.remove_roles(*[interaction.guild.get_role(role_id) for role_id in all_staff_role_ids], reason="Fired from staff by {}".format(interaction.user.display_name))
            await user.send(view=ui.LayoutView(timeout=0).add_item(UserFiredContainer(user, interaction.user, reason)))
            try:await (self.bot.get_guild(staff_server_id)).kick(user, reason="Fired from staff by {}".format(interaction.user.display_name))
            except Exception as e:
                log_exc(self._logger, e)
                self._logger.warning("Failed to kick user from staff server, they may still be there.")
            await interaction.response.send_message("`{}` fired successfully for: `{}`".format(user.display_name, reason if reason is not None else "No reason provided."), ephemeral=True)
        except Exception as e:
            log_exc(self._logger, e)
            await interaction.response.send_message("An error occurred while firing the user.\n"+codeblock_wrap(traceback.format_exception(e)), ephemeral=True)
    @staff.command(name="promote", description="Promotes a staff member to the next tier.")
    async def promote(self, interaction: discord.Interaction, user: discord.Member, reason: str = None):
        ptu = pt(interaction.user)
        ptt = pt(user)
        #~ begin block early return
        if not ptu.sr_administrative:
            return await interaction.response.send_message(noperm, ephemeral=True)
        if ptt.sr_administrative:
            return await interaction.response.send_message("You cannot promote this user, they are already at the highest permission tier they may attain.", ephemeral=True)
        if ptt.nstaff:
            return await interaction.response.send_message("You cannot promote this user, they are currently not a staff member, perhaps you want to `/hire` them?", ephemeral=True)
        if not ptu.owner and ptt.administrative:
            return await interaction.response.send_message("You cannot promote this user, they are at a higher or equal staff rank than you.", ephemeral=True)
        #~ finish block early return
        try:
            tier = ptt.tier
            self._log("{} promoted {} to {} (tier {})".format(interaction.user.display_name, user.display_name, pt.ttn(tier+1), tier+1))
            if tier == 5:
                for idx,server in enumerate((staff_server_id,main_server_id)):
                    await (self.bot.get_guild(server).get_member(user.id)).add_roles(interaction.guild.get_role(mod_role_ids[idx]), reason="Promoted to moderator by {}".format(interaction.user.display_name))
                    await (self.bot.get_guild(server).get_member(user.id)).remove_roles(interaction.guild.get_role(helper_role_ids[idx]), reason="Promoted from helper by {}".format(interaction.user.display_name))
            elif tier == 4:
                for idx,server in enumerate((staff_server_id,main_server_id)):
                    await (self.bot.get_guild(server).get_member(user.id)).add_roles(interaction.guild.get_role(sr_mod_role_ids[idx]), reason="Promoted to sr. mod by {}".format(interaction.user.display_name))
                    await (self.bot.get_guild(server).get_member(user.id)).remove_roles(interaction.guild.get_role(mod_role_ids[idx]), reason="Promoted from moderator by {}".format(interaction.user.display_name))
            elif tier == 3:
                for idx,server in enumerate((staff_server_id,main_server_id)):
                    await (self.bot.get_guild(server).get_member(user.id)).add_roles(interaction.guild.get_role(admin_role_ids[idx]), reason="Promoted to admin by {}".format(interaction.user.display_name))
                    await (self.bot.get_guild(server).get_member(user.id)).remove_roles(interaction.guild.get_role(sr_mod_role_ids[idx]), reason="Promoted from sr. mod by {}".format(interaction.user.display_name))
            elif tier == 2:
                for idx,server in enumerate((staff_server_id,main_server_id)):
                    await (self.bot.get_guild(server).get_member(user.id)).add_roles(interaction.guild.get_role(sr_admin_role_ids[idx]), reason="Promoted to sr. admin by {}".format(interaction.user.display_name))
                    await (self.bot.get_guild(server).get_member(user.id)).remove_roles(interaction.guild.get_role(admin_role_ids[idx]), reason="Promoted from admin by {}".format(interaction.user.display_name))
            await user.send(view=ui.LayoutView(timeout=0).add_item(UserPromotedContainer(user, interaction.user, tier+1, reason), timeout=0))
        except Exception as e:
            log_exc(self._logger, e)
            await interaction.response.send_message("An error occurred while promoting the user.\n"+codeblock_wrap(traceback.format_exception(e)), ephemeral=True)
    @staff.command(name="demote", description="Demotes a staff member to the previous tier.")
    async def demote(self, interaction: discord.Interaction, user: discord.Member, reason: str = None):
        ptu = pt(interaction.user)
        ptt = pt(user)
        #~ begin block early return
        if not ptu.sr_administrative:
            return await interaction.response.send_message(noperm, ephemeral=True)
        if not ptu.owner and ptt.sr_administrative:
            return await interaction.response.send_message("You cannot demote this user, they are at a higher or equal staff rank than you.", ephemeral=True)
        if ptt.nstaff:
            return await interaction.response.send_message("You cannot demote this user, they are currently not a staff member.", ephemeral=True)
        if ptt.helper:
            return await interaction.response.send_message("You cannot demote this user, they are already at the lowest staff rank possible, perhaps you wanted to `/fire` them?", ephemeral=True)
        #~ finish block early return
        try:
            tier = ptt.tier
            self._log("{} demoted {} to {} (tier {})".format(interaction.user.display_name, user.display_name, pt.ttn(tier-1), tier-1))
            if tier == 1:
                for idx,server in enumerate((staff_server_id,main_server_id)):
                    await (self.bot.get_guild(server).get_member(user.id)).remove_roles(interaction.guild.get_role(sr_admin_role_ids[idx]), reason="Demoted from sr. admin by {}".format(interaction.user.display_name))
                    await (self.bot.get_guild(server).get_member(user.id)).add_roles(interaction.guild.get_role(admin_role_ids[idx]), reason="Demoted to admin by {}".format(interaction.user.display_name))
            elif tier == 2:
                for idx,server in enumerate((staff_server_id,main_server_id)):
                    await (self.bot.get_guild(server).get_member(user.id)).remove_roles(interaction.guild.get_role(admin_role_ids[idx]), reason="Demoted from admin by {}".format(interaction.user.display_name))
                    await (self.bot.get_guild(server).get_member(user.id)).add_roles(interaction.guild.get_role(sr_mod_role_ids[idx]), reason="Demoted to sr. mod by {}".format(interaction.user.display_name))
            elif tier == 3:
                for idx,server in enumerate((staff_server_id,main_server_id)):
                    await (self.bot.get_guild(server).get_member(user.id)).remove_roles(interaction.guild.get_role(sr_mod_role_ids[idx]), reason="Demoted from sr. mod by {}".format(interaction.user.display_name))
                    await (self.bot.get_guild(server).get_member(user.id)).add_roles(interaction.guild.get_role(mod_role_ids[idx]), reason="Demoted to mod by {}".format(interaction.user.display_name))
            elif tier == 4:
                for idx,server in enumerate((staff_server_id,main_server_id)):
                    await (self.bot.get_guild(server).get_member(user.id)).remove_roles(interaction.guild.get_role(mod_role_ids[idx]), reason="Demoted from mod by {}".format(interaction.user.display_name))
                    await (self.bot.get_guild(server).get_member(user.id)).add_roles(interaction.guild.get_role(helper_role_ids[idx]), reason="Demoted to helper by {}".format(interaction.user.display_name))
            await user.send(view=ui.LayoutView(timeout=0).add_item(UserDemotedContainer(user, interaction.user, tier-1, reason), timeout=0))
            await interaction.response.send_message("`{}` demoted successfully for: `{}`".format(user.display_name, reason if reason is not None else "No reason provided."), ephemeral=True)
        except Exception as e:
            log_exc(self._logger, e)
            await interaction.response.send_message("An error occurred while demoting the user.\n"+codeblock_wrap(traceback.format_exception(e)), ephemeral=True)
    @app_commands.command(name="purge", description="Clears a specified number of messages from the current channel.")
    async def purge(self, interaction: discord.Interaction, amount: int):
        ptu = pt(interaction.user)
        #~ begin block early return
        if ptu.nstaff:
            return await interaction.response.send_message(noperm, ephemeral=True)
        maxi = 100 if ptu.moderative else 25
        maxi += 400 if ptu.administrative else 0
        maxi += 500 if ptu.owner else 0
        if amount < 1 or amount > maxi:
            return await interaction.response.send_message("The `amount` parameter must be between 1 and {}.".format(maxi), ephemeral=True)
        #~ finish block early return
        try:
            interaction.response.defer()
            await interaction.channel.purge(limit=amount,check=fresh)
            await interaction.followup.send("Cleared `{}` messages successfully!".format(amount), ephemeral=True)
            self._log("{} cleared {} messages from #{} ({})".format(interaction.user.display_name, amount, interaction.channel.name, interaction.guild.id))
        except Exception as e:
            log_exc(self._logger, e)
            await interaction.followup.send("An error occurred while clearing messages.\n"+codeblock_wrap(traceback.format_exception(e)), ephemeral=True)
    @app_commands.command(name="whoami", description="Shows information about you, or someone else.")
    async def whoami(self, interaction: discord.Interaction, user: discord.Member=None, advanced: bool=False):
        try:
            if advanced:
                await interaction.response.send_message(view=ui.LayoutView(WhoAmIContainer(user,advanced)),ephemeral=True,file=discord.File(io.BytesIO(await self.bot.get_cog("DatabaseModule").kv_bl_getdata(user.id)), filename="{}.bin".format(await self.bot.get_cog("DatabaseModule").kv_bl_hash(user.id))))
            else:
                await interaction.response.send_message(view=ui.LayoutView(WhoAmIContainer(user,advanced)),ephemeral=True)
        except Exception as e:
            log_exc(self._logger, e)
            await interaction.response.send_message("An error occurred while fetching your information.\n"+codeblock_wrap(traceback.format_exception(e)), ephemeral=True)
    @app_commands.command(name="bolo", description="Report a user to the be-on-the-lookout channel.")
    async def bolo(self, interaction: discord.Interaction, ign: str, username: str, id: str, reason: str = ""):
        ptu = pt(interaction.user)
        #~ begin block early return
        if ptu.moderative:
            return await interaction.response.send_message(noperm, ephemeral=True)
        #~ finish block early return
        try:
            await interaction.response.defer()
            await(self.bot.get_channel(bolo_channel_id)).send(view=ui.LayoutView(timeout=0).add_item(BoloContainer(ign, id, username, interaction.user.mention, reason)))
            await interaction.followup.send("New BOLO created successfully.", ephemeral=True)
        except Exception as e:
            log_exc(self._logger, e)
            await interaction.followup.send("An error occurred while creating the BOLO.\n"+codeblock_wrap(traceback.format_exception(e)), ephemeral=True)
    @steam.command(name="request", description="Submit a request to a higher-up staff rank.")
    @app_commands.choices(role=[
        app_commands.Choice(name="Helpers", value=helper_role_ids[0]),
        app_commands.Choice(name="Moderators", value=mod_role_ids[0]),
        app_commands.Choice(name="Sr. Moderators", value=sr_mod_role_ids[0]),
        app_commands.Choice(name="Administrators", value=admin_role_ids[0]),
        app_commands.Choice(name="Sr. Administrators", value=sr_admin_role_ids[0]),
        app_commands.Choice(name="Owner", value=owner_role_ids[0])
    ])
    async def request(self, interaction: discord.Interaction, rank: app_commands.Choice[int], message: str):
        #~ begin block early return
        if not pt(interaction.user).nstaff:
            return await interaction.response.send_message(noperm, ephemeral=True)
        #~ finish block early return
        try:
            cont = RankRequestContainer(interaction.user, rank.value, message)
            msg = await self.bot.get_channel(staff_requests_channel_id).send(view=ui.LayoutView(timeout=0).add_item(cont))
            thr = await msg.create_thread(auto_archive_duration=10080, name="Request from {}".format(interaction.user.display_name))
            await thr.send("The tagged rank and all other members of staff who are interested to discuss this request may do so here.")
            await interaction.response.send_message("Your request has been submitted to the requests channel.", ephemeral=True)
        except Exception as e:
            log_exc(self._logger, e)
            await interaction.response.send_message("An error occurred while submitting your request.\n"+codeblock_wrap(traceback.format_exception(e)), ephemeral=True)

async def setup(bot):
    cog = BasicSlashCommands(bot)
    await bot.add_cog(cog)
    cog._log(load_s)

##DEVNOTES:
## .format() and ondef type annotations are NOT used in an attempt to be
## in the very least compatible with older versions of python.
## This isn't required, and i will likely stop doing this in the future,
## but it's nice to have in case this project needs to be run on a machine supporting only older python versions.