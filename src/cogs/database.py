from discord.ext import commands
import os, dotenv, discord, logging, aiosqlite, hashlib
os.makedirs("/data/",exist_ok=True) #too much never hurts!
from src import bot_class
from fixedstr import *
def clamp_vol(v:int,t:int=150) -> int:
    return max(1,min(t,v))
class DatabaseModule(commands.Cog):
    def __init__(self, bot:bot_class.Bot, database_connection:aiosqlite.Connection):
        self.bot = bot
        os.makedirs("/data/",exist_ok=True)
        self.db=database_connection
        self._logger = logging.getLogger(self.__class__.__name__)
    def _log(self, msg:str):
        self._logger.info(msg)
    async def volume_set(self,gid:int,vol:int=100):
        vol=clamp_vol(vol)
        self.db.execute("INSERT INTO music_vol(guild,volume)VALUES(?,?)",(gid,vol))
    async def volume_get(self,gid:int):
        row = await(await self.db.execute("SELECT value FROM music_vol WHERE guild = ?",(gid,))).fetchone()
        return row[0] if row else 100
    async def kv_bl_exists(self,uid:int):
        row = await(await self.db.execute("SELECT value FROM kv_blacklist WHERE userid = ?",(uid,))).fetchone()
        return bool(row)
    async def kv_bl_setdata(self,uid:int,data:bytes):
        await self.db.execute("INSERT INTO kv_blacklist(userid,value)VALUES(?,?)",(uid,data))
    async def kv_bl_getdata(self,uid:int):
        row = await(await self.db.execute("SELECT value FROM kv_blacklist WHERE userid = ?",(uid,))).fetchone()
        return row[0] if row else b""
    async def kv_bl_del(self,uid:int):
        await self.db.execute("DELETE FROM kv_blacklist WHERE userid = ?",(uid,))
    async def kv_bl_hash(self,uid:int):
        row = await(await self.db.execute("SELECT value FROM kv_blacklist WHERE userid = ?",(uid,))).fetchone()
        data = row[0] if row else b""
        return hashlib.md5(data).hexdigest()

async def setup(bot):
    os.makedirs("/data/",exist_ok=True)
    conn=await aiosqlite.connect("/data/database.db")
    await conn.execute(open("/src/dbtables.sql").read())
    cog = DatabaseModule(bot, conn)
    await bot.add_cog(cog)
    cog._log(load_s)


##DEVNOTES:
## .format() and ondef type annotations are NOT used in an attempt to be
## in the very least compatible with older versions of python.
## This isn't required, and i will likely stop doing this in the future,
## but it's nice to have in case this project needs to be run on a machine supporting only older python versions.