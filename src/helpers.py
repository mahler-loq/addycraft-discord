
# Contains helper functions n stuff
import traceback,logging,discord.ui as ui,discord,cnst
from config import *
# Internal permission system helpers:

def determine_permission_tier(user:discord.Member):
    if any(role.id in cnst.owner_role_ids for role in user.roles):
        return 0
        # max permissions to developers, for testing purposes
    elif any(role.id in cnst.admin_role_ids for role in user.roles):
        return 1
    elif any(role.id in cnst.mod_role_ids for role in user.roles):
        return 2
    elif any(role.id in cnst.helper_role_ids for role in user.roles):
        return 3
    elif user.id in cnst.developers:
        if CONST_DEVELOPERS_MAXPERM_DEBUG:
            return 0
        else:
            return 2
    else:
        return 4

def name_to_tier(name:str):
    name = name.lower()
    if name in ["god", "owner"]:
        return 0
    elif name in ["admin", "administrator"]:
        return 1
    elif name in ["mod", "moderator"]:
        return 2
    elif name in ["helper", "staff"]:
        return 3
    elif name in ["user", "default"]:
        return 4
    else:
        raise ValueError("Invalid tier name: {}".format(name))
def tier_to_name(tier:int):
    if tier == 0:
        return "Owner"
    elif tier == 1:
        return "Admin"
    elif tier == 2:
        return "Moderator"
    elif tier == 3:
        return "Helper"
    elif tier == 4:
        return "User"
    else:
        raise ValueError("Invalid tier: {}".format(tier))

def is_god(user:discord.Member):
    return determine_permission_tier(user) == 0
def is_administrative(user:discord.Member):
    return determine_permission_tier(user) <= 1
def is_moderator(user:discord.Member):
    return determine_permission_tier(user) <= 2
def is_helper(user:discord.Member):
    return determine_permission_tier(user) <= 3
def is_helper_strict(user:discord.Member):
    return determine_permission_tier(user) == 3
def is_staff(user:discord.Member):
    if HELPERS_ARE_STAFF and not STRICT_SECURITY:
        return determine_permission_tier(user) <= 3
    else:
        return determine_permission_tier(user) <= 2
def is_not_staff(user:discord.Member):
    return determine_permission_tier(user) == 4

# Misc:

def codeblock_wrap(text:str|Exception|list[str], lang:str=""):
    if isinstance(text, Exception):text = "".join(traceback.format_exception(text))
    elif isinstance(text, list):text = "".join(text)
    else:text = str(text)
    return "```{0}\n{1}\n```".format(lang, text)

def log_exc(logger:logging.Logger,e:Exception):
    for i in "".join(traceback.format_exception(e)).splitlines():
        logger.error(i)