
# Contains helper functions n stuff
import traceback,logging,discord.ui as ui,discord,datetime
from . import cnst as cnst
from config import *
from fixedstr import *
# Internal permission system helpers:

class PermissionTier:
    def __init__(self,user:discord.Member):
        self.user=user
        self.DEV = CONST_DEVELOPERS_MAXPERM_DEBUG if user.id in cnst.developers else False
    @property
    def tier(self):
        user=self.user
        if any(role.id in cnst.owner_role_ids for role in user.roles):return 0
        elif any(role.id in cnst.sr_admin_role_ids for role in user.roles):return 1
        elif any(role.id in cnst.admin_role_ids for role in user.roles):return 2
        elif any(role.id in cnst.sr_mod_role_ids for role in user.roles):return 3
        elif any(role.id in cnst.mod_role_ids for role in user.roles):return 4
        elif any(role.id in cnst.helper_role_ids for role in user.roles):return 5
        else:return 6

    @property
    def name(self):
        match self.tier:
            case 0:return "Owner"
            case 1:return "Sr. Admin"
            case 2:return "Administrator"
            case 3:return "Sr. Moderator"
            case 4:return "Moderator"
            case 5:return "Helper"
            case _:return "User"

    # strict checks
    @property
    def owner(self):return self.tier==0
    @property
    def sradmin(self):return self.tier==1
    @property
    def admin(self):return self.tier==2
    @property
    def srmod(self):return self.tier==3
    @property
    def mod(self):return self.tier==4
    @property
    def helper(self):return self.tier==5
    @property
    def not_staff(self):return self.tier==6
    @property
    def nstaff(self):return self.tier==6

    # broad checks
    @property
    def staff(self):return self.tier!=6 or self.DEV
    @property
    def moderative(self):return self.tier<=4 or self.DEV
    @property
    def sr_moderative(self):return self.tier<=3 or self.DEV
    @property
    def administrative(self):return self.tier<=2 or self.DEV
    @property
    def sr_administrative(self):return self.tier<=1 or self.DEV

    # special checks
    def dj(self):
        return any(role.id in cnst.dj_role_ids for role in self.user.roles) or self.sr_moderative
    @property
    def developer(self):
        return any(role.id in cnst.developer_role_ids for role in self.user.roles)
    @property
    def builder(self):
        return any(role.id in cnst.builder_role_ids for role in self.user.roles)
    @property
    def artist(self):
        return any(role.id in cnst.artist_role_ids for role in self.user.roles)
    @property
    def DEV(self):
        return self.cond
    
    # utility static methods
    @staticmethod
    def ttn(tier:int):
        match tier:
            case 0:return "Owner"
            case 1:return "Sr. Admin"
            case 2:return "Administrator"
            case 3:return "Sr. Moderator"
            case 4:return "Moderator"
            case 5:return "Helper"
            case _:return "User"

    # other
    @property
    def special_pretty(self):
        return PCD
        x=[]
        if self.developer:x.append("Developer")
        if self.dj:x.append("DJ")
        if self.builder:x.append("Builder")
        if self.artist:x.append("Artist")
        return ", ".join(x) if x else "None"

# Misc:

def codeblock_wrap(text:str|Exception|list[str],lang:str=""):
    if isinstance(text,Exception):text = "".join(traceback.format_exception(text))
    elif isinstance(text,list):text = "".join(text)
    else:text = str(text)
    return "```{0}\n{1}\n```".format(lang,text)

def log_exc(logger:logging.Logger,e:Exception):
    for i in "".join(traceback.format_exception(e)).splitlines():
        logger.error(i)
        
def fresh(message:discord.Message):
    return discord.utils.utcnow() - message.created_at > datetime.timedelta(weeks=2)