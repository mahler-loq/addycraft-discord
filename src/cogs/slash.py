import traceback
from discord.ext import commands
from discord import app_commands
import os, dotenv, discord, logging, discord.ui as ui
from src.helpers import *
from src.cnst import *
import src.bot_class as bot_class
class SeparatedTextContainer(ui.Container):
    def __init__(self, title:str, text:str, ping:discord.Role|discord.User=None, author:str=None):
        super().__init__()
        self.title = title
        self.text = text
        self.ping = ping.mention
        if ping is not None:
            self.add_item(ui.TextDisplay(content=self.ping))
            self.add_item(ui.Separator())
        self.add_item(ui.TextDisplay(content="### "+self.title))
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
        self.add_item(ui.TextDisplay(content="### Application approved!"))
        self.add_item(ui.Separator())
        self.add_item(ui.TextDisplay(content="""Congratulations, {}\n\nYour application has been approved by {}. Thank you so much for your consideration in joining the staff team and we really look forward to working with you. Below will be a link to our Staff Discord Server.""".format(self.user.mention, self.author.mention)))
        self.add_item(ui.Separator())
        self.add_item(ui.Button(label="Join the Staff Server", url=url, style=discord.ButtonStyle.success))
class UserFiredContainer(ui.Container):
    def __init__(self, user:discord.Member, author:discord.Member, reason:str=None):
        super().__init__()
        self.user = user
        self.author = author
        self.add_item(ui.TextDisplay(content="### Staff Position Terminated"))
        self.add_item(ui.Separator())
        self.add_item(ui.TextDisplay("""We regret to inform you that your position on the staff team has been terminated by {}.\n\nReason:\n{}\n\nIf you have any questions regarding this decision, please feel free to reach out to any of the current staff members for more information.""".format(self.author.mention, reason if reason is not None else "No reason provided.")))
class UserPromotedContainer(ui.Container):
    def __init__(self, user:discord.Member, author:discord.Member, new:int, reason:str):
        super().__init__()
        self.user = user
        self.author = author
        self.new = new
        self.reason = reason
        self.add_item(ui.TextDisplay(content="### Staff Position Promoted"))
        self.add_item(ui.Separator())
        self.add_item(ui.TextDisplay(content="Congratulations, {}!\n\nYou have been promoted to `{}` by {}.\n\nReason:\n{}".format(self.user.mention, tier_to_name(self.new), self.author.mention, self.reason if self.reason is not None else "No reason provided.")))
class UserDemotedContainer(ui.Container):
    def __init__(self, user:discord.Member, author:discord.Member, new:int, reason:str):
        super().__init__()
        self.user = user
        self.author = author
        self.new = new
        self.reason = reason
        self.add_item(ui.TextDisplay(content="### Staff Position Demoted"))
        self.add_item(ui.Separator())
        self.add_item(ui.TextDisplay(content="We regret to inform you that you have been demoted to `{}` by {}.\n\nReason:\n{}".format(tier_to_name(self.new), self.author.mention, self.reason if self.reason is not None else "No reason provided.")))
class BasicSlashCommands(commands.Cog):
    def __init__(self, bot:bot_class.Bot):
        self.bot = bot
        self._logger = logging.getLogger(self.__class__.__name__)
    def _log(self, msg:str):
        self._logger.info(msg)
    @app_commands.command(name="announce", description="Sends an announcement to the specified channel, optionally pinging a role.")
    async def announce(self, interaction: discord.Interaction, channel: discord.TextChannel, title: str, text: str, ping: discord.Role = None):
        #~ begin block early return
        if not is_god(interaction.user):
            return await interaction.response.send_message(noperm, ephemeral=True)
        #~ finish block early return
        try:
            cont = SeparatedTextContainer(title, text, ping, interaction.user.display_name)
            await channel.send(view=ui.LayoutView(cont,timeout=0))
            await interaction.response.send_message("Announcement sent successfully!", ephemeral=True)
        except Exception as e:
            log_exc(self._logger, e)
            await interaction.response.send_message("An error occurred while sending the announcement.\n"+codeblock_wrap(traceback.format_exception(e)), ephemeral=True)
    @app_commands.command(name="hire", description="Hires a user as a helper.")
    async def hire(self, interaction: discord.Interaction, user: discord.Member):
        #~ begin block early return
        if not is_administrative(interaction.user):
            return await interaction.response.send_message(noperm, ephemeral=True)
        if is_staff(user):
            return await interaction.response.send_message("User is already apart of staff, perhaps you meant to `/promote` them?", ephemeral=True)
        #~ finish block early return
        try:
            self._log("{} hired {}".format(interaction.user.display_name, user.display_name))
            url=(await(self.bot.get_channel(staff_entry_channel_id)).create_invite(max_uses=1, max_age=0)).url
            await user.send(view=ui.LayoutView(UserHiredContainer(user, interaction.user, url),timeout=0))
            await user.add_roles(interaction.guild.get_role(helper_role_ids[0]), reason="Hired as helper by {}".format(interaction.user.display_name))
        except Exception as e:
            log_exc(self._logger, e)
            return await interaction.response.send_message("An error occurred while hiring the user.\n"+codeblock_wrap(traceback.format_exception(e)), ephemeral=True)
        await interaction.response.send_message("`{}` hired successfully! Make sure to remember to manually give them their `Helper` rank when they join the staff server.".format(user.display_name), ephemeral=True)
    @app_commands.command(name="fire", description="Fires a user from their staff position.")
    async def fire(self, interaction: discord.Interaction, user: discord.Member, reason: str = None):
        #~ begin block early return
        if not is_administrative(interaction.user):
            return await interaction.response.send_message(noperm, ephemeral=True)
        if is_administrative(user) and not is_god(interaction.user):
            return await interaction.response.send_message("You cannot fire this user, they are at a higher or equal staff rank than you.", ephemeral=True)
        if is_not_staff(user) and not is_helper_strict(user):
            return await interaction.response.send_message("You cannot fire this user, they are currently not a staff member.", ephemeral=True)
        #~ finish block early return
        try:
            self._log("{} fired {}".format(interaction.user.display_name, user.display_name))
            await user.remove_roles(*[interaction.guild.get_role(role_id) for role_id in helper_role_ids+mod_role_ids+admin_role_ids+owner_role_ids], reason="Fired from staff by {}".format(interaction.user.display_name))
            await user.send(view=ui.LayoutView(UserFiredContainer(user, interaction.user, reason), timeout=0))
            try:await (self.bot.get_guild(staff_server_id)).kick(user, reason="Fired from staff by {}".format(interaction.user.display_name))
            except Exception as e:
                log_exc(self._logger, e)
                self._logger.warning("Failed to kick user from staff server, they may still be there.")
            await interaction.response.send_message("`{}` fired successfully for: `{}`".format(user.display_name, reason if reason is not None else "No reason provided."), ephemeral=True)
        except Exception as e:
            log_exc(self._logger, e)
            await interaction.response.send_message("An error occurred while firing the user.\n"+codeblock_wrap(traceback.format_exception(e)), ephemeral=True)
    @app_commands.command(name="promote", description="Promotes a staff member to the next tier.")
    async def promote(self, interaction: discord.Interaction, user: discord.Member, reason: str = None):
        #~ begin block early return
        if not is_administrative(interaction.user):
            return await interaction.response.send_message(noperm, ephemeral=True)
        if is_administrative(user):
            return await interaction.response.send_message("You cannot promote this user, they are already at the highest permission tier they may attain.", ephemeral=True)
        if is_not_staff(user):
            return await interaction.response.send_message("You cannot promote this user, they are currently not a staff member, perhaps you want to `/hire` them?", ephemeral=True)
        #~ finish block early return
        try:
            tier = determine_permission_tier(user)
            self._log("{} promoted {} to {} (tier {})".format(interaction.user.display_name, user.display_name, tier_to_name(tier+1), tier+1))
            if tier == 3:
                for idx,server in enumerate((staff_server_id,main_server_id)):
                    await (self.bot.get_guild(server).get_member(user.id)).add_roles(interaction.guild.get_role(mod_role_ids[idx]), reason="Promoted to moderator by {}".format(interaction.user.display_name))
                    await (self.bot.get_guild(server).get_member(user.id)).remove_roles(interaction.guild.get_role(helper_role_ids[idx]), reason="Promoted from helper by {}".format(interaction.user.display_name))
            elif tier == 2:
                for idx,server in enumerate((staff_server_id,main_server_id)):
                    await (self.bot.get_guild(server).get_member(user.id)).add_roles(interaction.guild.get_role(admin_role_ids[idx]), reason="Promoted to admin by {}".format(interaction.user.display_name))
                    await (self.bot.get_guild(server).get_member(user.id)).remove_roles(interaction.guild.get_role(mod_role_ids[idx]), reason="Promoted from moderator by {}".format(interaction.user.display_name))
            await user.send(view=ui.LayoutView(UserPromotedContainer(user, interaction.user, tier+1, reason), timeout=0))
        except Exception as e:
            log_exc(self._logger, e)
            await interaction.response.send_message("An error occurred while promoting the user.\n"+codeblock_wrap(traceback.format_exception(e)), ephemeral=True)
    @app_commands.command(name="demote", description="Demotes a staff member to the previous tier.")
    async def demote(self, interaction: discord.Interaction, user: discord.Member, reason: str = None):
        #~ begin block early return
        if not is_administrative(interaction.user):
            return await interaction.response.send_message(noperm, ephemeral=True)
        if is_administrative(user) and not is_god(interaction.user):
            return await interaction.response.send_message("You cannot demote this user, they are at a higher or equal staff rank than you.", ephemeral=True)
        if is_not_staff(user):
            return await interaction.response.send_message("You cannot demote this user, they are currently not a staff member.", ephemeral=True)
        if is_helper_strict(user):
            return await interaction.response.send_message("You cannot demote this user, they are already at the lowest staff rank possible, perhaps you wanted to `/fire` them?", ephemeral=True)
        #~ finish block early return
        try:
            tier = determine_permission_tier(user)
            self._log("{} demoted {} to {} (tier {})".format(interaction.user.display_name, user.display_name, tier_to_name(tier-1), tier-1))
            if tier == 1:
                for idx,server in enumerate((staff_server_id,main_server_id)):
                    await (self.bot.get_guild(server).get_member(user.id)).remove_roles(interaction.guild.get_role(admin_role_ids[idx]), reason="Demoted from admin by {}".format(interaction.user.display_name))
                    await (self.bot.get_guild(server).get_member(user.id)).add_roles(interaction.guild.get_role(mod_role_ids[idx]), reason="Demoted to moderator by {}".format(interaction.user.display_name))
            elif tier == 2:
                for idx,server in enumerate((staff_server_id,main_server_id)):
                    await (self.bot.get_guild(server).get_member(user.id)).remove_roles(interaction.guild.get_role(mod_role_ids[idx]), reason="Demoted from moderator by {}".format(interaction.user.display_name))
                    await (self.bot.get_guild(server).get_member(user.id)).add_roles(interaction.guild.get_role(helper_role_ids[idx]), reason="Demoted to helper by {}".format(interaction.user.display_name))
            await user.send(view=ui.LayoutView(UserDemotedContainer(user, interaction.user, tier-1, reason), timeout=0))
            await interaction.response.send_message("`{}` demoted successfully for: `{}`".format(user.display_name, reason if reason is not None else "No reason provided."), ephemeral=True)
        except Exception as e:
            log_exc(self._logger, e)
            await interaction.response.send_message("An error occurred while demoting the user.\n"+codeblock_wrap(traceback.format_exception(e)), ephemeral=True)
    @app_commands.command(name="purge", description="Clears a specified number of messages from the current channel.")
    async def purge(self, interaction: discord.Interaction, amount: int):
        #~ begin block early return
        if not is_moderator(interaction.user):
            return await interaction.response.send_message(noperm, ephemeral=True)
        if amount < 1 or amount > 100:
            return await interaction.response.send_message("Please specify an amount between 1 and 100.", ephemeral=True)
        #~ finish block early return
        try:
            interaction.response.defer()
            await interaction.channel.purge(limit=amount)
            await interaction.followup.send("Cleared `{}` messages successfully!".format(amount), ephemeral=True)
            self._log("{} cleared {} messages from #{} ({})".format(interaction.user.display_name, amount, interaction.channel.name, interaction.guild.id))
        except Exception as e:
            log_exc(self._logger, e)
            await interaction.followup.send("An error occurred while clearing messages.\n"+codeblock_wrap(traceback.format_exception(e)), ephemeral=True)
    @app_commands.command(name="whoami", description="Shows information about you, or someone else.")
    async def whoami(self, interaction: discord.Interaction, user: discord.Member=None):
        try:
            if user is None:
                user = interaction.user
            message = "Your display name: `{}`\nYour ID: `{}`\nYour permission tier: `{} ({})`".format(user.display_name, user.id, tier_to_name(determine_permission_tier(user)), determine_permission_tier(user))
            await interaction.response.send_message(message, ephemeral=True)
        except Exception as e:
            log_exc(self._logger, e)
            await interaction.response.send_message("An error occurred while fetching your information.\n"+codeblock_wrap(traceback.format_exception(e)), ephemeral=True)

async def setup(bot):
    cog = BasicSlashCommands(bot)
    await bot.add_cog(cog)
    cog._log("loaded successfully!")

##DEVNOTES:
## .format() and ondef type annotations are NOT used in an attempt to be
## in the very least compatible with older versions of python.
## This isn't required, and i will likely stop doing this in the future,
## but it's nice to have in case this project needs to be run on a machine supporting only older python versions.