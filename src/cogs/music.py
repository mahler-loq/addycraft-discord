from discord.ext import commands
from discord import FFmpegOpusAudio, app_commands
import os, dotenv, discord, asyncio, logging, yt_dlp, ffmpeg
from src import bot_class
from fixedstr import *
from src.cnst import *
from collections import deque
from src.helpers import *
def _extract(query:str, ytdlp_opts:dict):
    with yt_dlp.YoutubeDL(ytdlp_opts) as ytdlp:
        return ytdlp.extract_info(query, download=False)

class Music(commands.Cog):
    music = app_commands.Group(name="music", description="Music commands")
    def __init__(self, bot:bot_class.Bot):
        self.bot = bot
        self.ytdlp_opts = {
            "format": "bestaudio[abr<=96]/bestaudio",
            "noplaylist": True,
            "youtube_include_dash_manifest": False,
            "youtube_include_hls_manifest": False,
            "nocheckcertificate": True,
            "quiet": True,
            "no_warnings": True
        }
        self.ffmpeg_opts = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            "options": "-vn -c:a libopus -b:a 96k -loglevel quiet"
        }
        self.queues = {}
        self._logger = logging.getLogger(self.__class__.__name__)
    def _log(self, msg:str):
        self._logger.info(msg)
    async def search_youtube(self, query:str):
        return await(asyncio.get_running_loop()).run_in_executor(None, _extract, query, self.ytdlp_opts)
    async def broadcast_queue_update(self, message:str, id:int):
        message="[**{}**] {}".format(self.bot.get_guild(id).name if self.bot.get_guild(id) else "Unknown server", message)
        await asyncio.gather(*[self.bot.get_channel(id).send(message)for id in music_queue_channel_ids if self.bot.get_channel(id)],return_exceptions=True)
    async def play_next(self, voice_client:discord.VoiceClient, guild_id:int):
        if self.queues.get(guild_id):
            url,title=self.queues[guild_id].popleft()
            source = FFmpegOpusAudio(url, **self.ffmpeg_opts)
            def after_playing(error):
                if error:
                    self._log("Error playing audio: {}".format(error))
                asyncio.run_coroutine_threadsafe(self.play_next(voice_client, guild_id), self.bot.loop)
            voice_client.play(source,after=after_playing)
            asyncio.create_task(self.broadcast_queue_update("Now playing: **{}**".format(title),guild_id))
        else:
            await self.broadcast_queue_update("Queue is empty, leaving voice channel.",guild_id)
            await voice_client.disconnect()
            self.queues[guild_id] = deque()
    @music.command(name="play", description="Plays a song from youtube")
    async def play(self, interaction:discord.Interaction, query:str):
        await interaction.response.defer()
        self._log("play command invoked with query: {}".format(query))
        #~ begin block early return
        if not is_dj(interaction.user):return interaction.response.send_message(no_dj,ephemeral=True)
        if interaction.user.voice is None:
            return await interaction.followup.send("You must be in a voice channel to use this command.",ephemeral=True)
        vc = interaction.user.voice.channel
        if interaction.guild.voice_client is None:
            voice_client = await vc.connect()
        elif interaction.guild.voice_client.channel != vc:
            return await interaction.response.send_message("I'm already connected to a voice channel in this server, please use the /leave command to disconnect me from it first.",ephemeral=True)
        #~ finish block early return
        query="ytsearch1:{}".format(query)
        results = await self.search_youtube(query)
        tracks = results.get("entries", [])
        if not tracks:
            return await interaction.followup.send("No results found for your query.",ephemeral=True)
        track=tracks[0]
        url=track.get("url")
        title=track.get("title","Unknown Title")
        gid=interaction.guild_id
        if self.queues.get(gid) is None:
            self.queues[gid] = deque()
        self.queues[gid].append((url,title))
        if voice_client.is_playing() or voice_client.is_paused():
            await interaction.followup.send("Added **{}** to the queue.".format(title))
        else:
            await interaction.followup.send("Playing **{}**.".format(title))
            await self.play_next(voice_client, interaction.guild_id)
    @music.command(name="skip", description="Skips the currently playing song")
    async def skip(self, interaction:discord.Interaction):
        #~ begin block early return
        if not is_dj(interaction.user):return interaction.response.send_message(no_dj,ephemeral=True)
        #~ finish block early return
        if interaction.guild.voice_client and (interaction.guild.voice_client.is_playing() or interaction.guild.voice_client.is_paused()):
            interaction.guild.voice_client.stop()
            await interaction.response.send_message("Skipped the current song.")
        else:
            await interaction.response.send_message("No song is currently playing.",ephemeral=True)
    @music.command(name="pause", description="Pauses the currently playing song")
    async def pause(self, interaction:discord.Interaction):
        voice_client = interaction.guild.voice_client
        #~ begin block early return
        if not is_dj(interaction.user):return interaction.response.send_message(no_dj,ephemeral=True)
        if voice_client is None:
            return await interaction.response.send_message(no_vcl,ephemeral=True)
        if not voice_client.is_playing():
            return await interaction.response.send_message("No song is currently playing.",ephemeral=True)
        #~ finish block early return
        voice_client.pause()
        await interaction.response.send_message("Paused the current song.")
    @music.command(name="resume", description="Resumes a paused song")
    async def resume(self, interaction:discord.Interaction):
        voice_client = interaction.guild.voice_client
        #~ begin block early return
        if not is_dj(interaction.user):return interaction.response.send_message(no_dj,ephemeral=True)
        if voice_client is None:
            return await interaction.response.send_message(no_vcl,ephemeral=True)
        if not voice_client.is_paused():
            return await interaction.response.send_message("No song is currently paused.",ephemeral=True)
        #~ finish block early return
        voice_client.resume()
        await interaction.response.send_message("Resumed the current song.")
    @music.command(name="queue", description="Shows the current music queue")
    async def queue(self, interaction: discord.Interaction):
        gid = interaction.guild_id
        if not is_dj(interaction.user):return interaction.response.send_message(no_dj,ephemeral=True)
        if gid not in self.queues or not self.queues[gid]:
            return await interaction.response.send_message("The queue is currently empty.", ephemeral=True)
        queue = list(self.queues[gid])
        msg = "\n".join("[{}] **{}**".format(i+1,title)for i,(_,title)in enumerate(queue[:10]))
        if len(queue) > 10:
            msg += "\n...and {} more.".format(len(queue)-10)
        await interaction.response.send_message("Current queue:\n{}".format(msg))
    @music.command(name="stop", description="Leaves the voice channel and clears the queue")
    async def stop(self, interaction:discord.Interaction):
        await interaction.response.defer()
        voice_client = interaction.guild.voice_client
        #~ begin block early return
        if not is_dj(interaction.user):return interaction.response.send_message(no_dj,ephemeral=True)
        if not voice_client:
            return await interaction.followup.send(no_vcl,ephemeral=True)
        #~ finish block early return
        if interaction.guild_id in self.queues:
            self.queues[interaction.guild_id].clear()
        if voice_client.is_playing() or voice_client.is_paused():
            voice_client.stop()
        await interaction.followup.send("Stopped playback.")
    @music.command(name="leave", description="Disconnects the bot from the voice channel")
    async def leave(self, interaction:discord.Interaction):
        await interaction.response.defer()
        voice_client = interaction.guild.voice_client
        #~ begin block early return
        if not is_dj(interaction.user):return interaction.response.send_message(no_dj,ephemeral=True)

        if not voice_client:
            return await interaction.followup.send(no_vcl,ephemeral=True)
        #~ finish block early return
        if interaction.guild_id in self.queues:
            self.queues[interaction.guild_id].clear()
        if voice_client.is_playing() or voice_client.is_paused():
            voice_client.stop()
        await voice_client.disconnect()
        await interaction.followup.send("Disconnected from the voice channel.")
async def setup(bot):
    cog = Music(bot)
    await bot.add_cog(cog)
    cog._log(load_s)

##DEVNOTES:
## .format() and ondef type annotations are NOT used in an attempt to be
## in the very least compatible with older versions of python.
## This isn't required, and i will likely stop doing this in the future,
## but it's nice to have in case this project needs to be run on a machine supporting only older python versions.